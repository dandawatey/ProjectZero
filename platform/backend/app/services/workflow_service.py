from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.stage_gates import validate_stage_transition, StageGateError
from app.models.workflow import (
    WorkflowRun,
    WorkflowStep,
    WorkflowApproval,
    WorkflowArtifact,
    WorkflowAudit,
    WorkflowTrigger,
    AgentContribution,
)
from app.schemas.workflow import (
    WorkflowRunCreate,
    StepSyncRequest,
    WorkflowApprovalCreate,
    ApprovalResolve,
    AgentContributionCreate,
    WorkflowArtifactCreate,
    WorkflowAuditCreate,
    WorkflowTriggerCreate,
    WorkflowTriggerUpdate,
    DashboardSummary,
    WorkflowAuditRead,
)
from app.temporal_integration import client as temporal

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Workflow Runs
# ---------------------------------------------------------------------------

async def create_workflow_run(db: AsyncSession, data: WorkflowRunCreate) -> WorkflowRun:
    run = WorkflowRun(
        id=uuid.uuid4(),
        workflow_type=data.workflow_type,
        feature_id=data.feature_id,
        product_id=data.product_id,
        status="pending",
        current_stage=None,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def get_workflow_run(db: AsyncSession, run_id: uuid.UUID) -> WorkflowRun | None:
    return await db.get(WorkflowRun, run_id)


async def list_workflow_runs(
    db: AsyncSession,
    *,
    status: str | None = None,
    workflow_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[WorkflowRun], int]:
    q = select(WorkflowRun).order_by(WorkflowRun.created_at.desc())
    count_q = select(func.count(WorkflowRun.id))

    if status:
        q = q.where(WorkflowRun.status == status)
        count_q = count_q.where(WorkflowRun.status == status)
    if workflow_type:
        q = q.where(WorkflowRun.workflow_type == workflow_type)
        count_q = count_q.where(WorkflowRun.workflow_type == workflow_type)

    total = (await db.execute(count_q)).scalar_one()
    rows = (await db.execute(q.limit(limit).offset(offset))).scalars().all()
    return list(rows), total


async def update_workflow_state(
    db: AsyncSession,
    feature_id: str,
    status: str,
    stage: str | None = None,
) -> WorkflowRun | None:
    """Idempotent state update keyed by feature_id."""
    result = await db.execute(
        select(WorkflowRun).where(WorkflowRun.feature_id == feature_id).order_by(WorkflowRun.created_at.desc())
    )
    run = result.scalars().first()
    if run is None:
        return None

    if stage is not None:
        validate_stage_transition(run.current_stage, stage)
        run.current_stage = stage
    run.status = status
    run.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(run)
    return run


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

async def record_step(db: AsyncSession, data: StepSyncRequest) -> WorkflowStep:
    """Idempotent step recording keyed by correlation_id."""
    # Check for existing step with this correlation_id
    if data.correlation_id:
        existing = await db.execute(
            select(WorkflowStep).where(WorkflowStep.correlation_id == data.correlation_id)
        )
        step = existing.scalars().first()
        if step is not None:
            # Update status if changed
            step.status = data.status
            if data.status in ("completed", "failed"):
                step.completed_at = datetime.now(timezone.utc)
            if data.error_message:
                step.error_message = data.error_message
            await db.commit()
            await db.refresh(step)
            return step

    # Find the workflow run by feature_id
    result = await db.execute(
        select(WorkflowRun).where(WorkflowRun.feature_id == data.feature_id).order_by(WorkflowRun.created_at.desc())
    )
    run = result.scalars().first()
    if run is None:
        raise ValueError(f"No workflow run found for feature_id={data.feature_id}")

    now = datetime.now(timezone.utc)
    step = WorkflowStep(
        id=uuid.uuid4(),
        workflow_run_id=run.id,
        stage_name=data.stage_name,
        status=data.status,
        agent_type=data.agent_type,
        agent_id=data.agent_id,
        correlation_id=data.correlation_id,
        started_at=now,
        completed_at=now if data.status in ("completed", "failed") else None,
        error_message=data.error_message,
    )
    db.add(step)
    await db.commit()
    await db.refresh(step)
    return step


async def get_steps_for_run(db: AsyncSession, workflow_run_id: uuid.UUID) -> list[WorkflowStep]:
    result = await db.execute(
        select(WorkflowStep)
        .where(WorkflowStep.workflow_run_id == workflow_run_id)
        .order_by(WorkflowStep.started_at.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Approvals
# ---------------------------------------------------------------------------

async def create_approval_request(db: AsyncSession, data: WorkflowApprovalCreate) -> WorkflowApproval:
    approval = WorkflowApproval(
        id=uuid.uuid4(),
        workflow_run_id=data.workflow_run_id,
        stage_name=data.stage_name,
        approval_type=data.approval_type,
        status="pending",
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return approval


async def resolve_approval(
    db: AsyncSession,
    approval_id: uuid.UUID,
    data: ApprovalResolve,
) -> WorkflowApproval | None:
    approval = await db.get(WorkflowApproval, approval_id)
    if approval is None:
        return None
    approval.status = data.status
    approval.resolved_at = datetime.now(timezone.utc)
    approval.resolved_by = data.resolved_by
    await db.commit()
    await db.refresh(approval)
    return approval


async def list_pending_approvals(db: AsyncSession) -> list[WorkflowApproval]:
    result = await db.execute(
        select(WorkflowApproval)
        .where(WorkflowApproval.status == "pending")
        .order_by(WorkflowApproval.requested_at.asc())
    )
    return list(result.scalars().all())


async def get_approvals_for_run(db: AsyncSession, workflow_run_id: uuid.UUID) -> list[WorkflowApproval]:
    result = await db.execute(
        select(WorkflowApproval)
        .where(WorkflowApproval.workflow_run_id == workflow_run_id)
        .order_by(WorkflowApproval.requested_at.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Agent Contributions
# ---------------------------------------------------------------------------

async def record_agent_contribution(db: AsyncSession, data: AgentContributionCreate) -> AgentContribution:
    contrib = AgentContribution(
        id=uuid.uuid4(),
        workflow_run_id=data.workflow_run_id,
        step_id=data.step_id,
        agent_type=data.agent_type,
        agent_id=data.agent_id,
        action=data.action,
        result=data.result,
        duration_ms=data.duration_ms,
    )
    db.add(contrib)
    await db.commit()
    await db.refresh(contrib)
    return contrib


async def get_contributions_for_run(db: AsyncSession, workflow_run_id: uuid.UUID) -> list[AgentContribution]:
    result = await db.execute(
        select(AgentContribution)
        .where(AgentContribution.workflow_run_id == workflow_run_id)
        .order_by(AgentContribution.created_at.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------

async def create_artifact(db: AsyncSession, data: WorkflowArtifactCreate) -> WorkflowArtifact:
    artifact = WorkflowArtifact(
        id=uuid.uuid4(),
        workflow_run_id=data.workflow_run_id,
        stage_name=data.stage_name,
        artifact_type=data.artifact_type,
        content_path=data.content_path,
        metadata_=data.metadata,
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    return artifact


async def get_artifacts_for_run(db: AsyncSession, workflow_run_id: uuid.UUID) -> list[WorkflowArtifact]:
    result = await db.execute(
        select(WorkflowArtifact)
        .where(WorkflowArtifact.workflow_run_id == workflow_run_id)
        .order_by(WorkflowArtifact.created_at.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

async def create_audit_entry(db: AsyncSession, data: WorkflowAuditCreate) -> WorkflowAudit:
    entry = WorkflowAudit(
        workflow_run_id=data.workflow_run_id,
        action=data.action,
        agent_id=data.agent_id,
        details=data.details,
        correlation_id=data.correlation_id,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_audit_for_run(db: AsyncSession, workflow_run_id: uuid.UUID) -> list[WorkflowAudit]:
    result = await db.execute(
        select(WorkflowAudit)
        .where(WorkflowAudit.workflow_run_id == workflow_run_id)
        .order_by(WorkflowAudit.created_at.desc())
    )
    return list(result.scalars().all())


async def list_audit_entries(db: AsyncSession, limit: int = 100, offset: int = 0) -> list[WorkflowAudit]:
    result = await db.execute(
        select(WorkflowAudit).order_by(WorkflowAudit.created_at.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

async def get_dashboard_summary(db: AsyncSession) -> DashboardSummary:
    async def _count(status: str) -> int:
        r = await db.execute(select(func.count(WorkflowRun.id)).where(WorkflowRun.status == status))
        return r.scalar_one()

    active = await _count("running")
    completed = await _count("completed")
    failed = await _count("failed")
    blocked = await _count("blocked")

    recent = await db.execute(
        select(WorkflowAudit).order_by(WorkflowAudit.created_at.desc()).limit(20)
    )
    recent_rows = recent.scalars().all()

    return DashboardSummary(
        active=active,
        completed=completed,
        failed=failed,
        blocked=blocked,
        recent_activity=[WorkflowAuditRead.model_validate(r) for r in recent_rows],
    )


# ---------------------------------------------------------------------------
# Triggers
# ---------------------------------------------------------------------------

async def create_trigger(db: AsyncSession, data: WorkflowTriggerCreate) -> WorkflowTrigger:
    trigger = WorkflowTrigger(
        id=uuid.uuid4(),
        workflow_type=data.workflow_type,
        trigger_type=data.trigger_type,
        config=data.config,
        is_active=data.is_active,
    )
    db.add(trigger)
    await db.commit()
    await db.refresh(trigger)
    return trigger


async def list_triggers(db: AsyncSession) -> list[WorkflowTrigger]:
    result = await db.execute(select(WorkflowTrigger).order_by(WorkflowTrigger.created_at.desc()))
    return list(result.scalars().all())


async def update_trigger(db: AsyncSession, trigger_id: uuid.UUID, data: WorkflowTriggerUpdate) -> WorkflowTrigger | None:
    trigger = await db.get(WorkflowTrigger, trigger_id)
    if trigger is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(trigger, field, value)
    await db.commit()
    await db.refresh(trigger)
    return trigger


async def delete_trigger(db: AsyncSession, trigger_id: uuid.UUID) -> bool:
    trigger = await db.get(WorkflowTrigger, trigger_id)
    if trigger is None:
        return False
    await db.delete(trigger)
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Temporal integration
# ---------------------------------------------------------------------------

async def start_temporal_workflow(
    db: AsyncSession,
    run: WorkflowRun,
    config: dict[str, Any] | None = None,
) -> str:
    """Start a Temporal workflow for the given run, store run_id back."""
    workflow_id = f"pz-{run.workflow_type}-{run.id}"
    args = [
        {
            "workflow_run_id": str(run.id),
            "feature_id": run.feature_id,
            "product_id": run.product_id,
            "workflow_type": run.workflow_type,
            **(config or {}),
        }
    ]
    temporal_run_id = await temporal.start_workflow(
        workflow_name=f"{run.workflow_type}Workflow",
        workflow_id=workflow_id,
        args=args,
    )
    run.temporal_run_id = temporal_run_id
    run.status = "running"
    await db.commit()
    await db.refresh(run)
    return temporal_run_id
