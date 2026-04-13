from __future__ import annotations

import uuid
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workflow import (
    WorkflowRunCreate,
    WorkflowRunRead,
    WorkflowRunList,
    WorkflowSignal,
    WorkflowStepRead,
    WorkflowCatalogEntry,
)
from app.core.stage_gates import next_stage as _next_stage, is_terminal, STAGE_ORDER
from app.services import workflow_service as svc
from app.temporal_integration import client as temporal

logger = logging.getLogger(__name__)
router = APIRouter()

# Static catalog — extend as workflow types grow
WORKFLOW_CATALOG: list[WorkflowCatalogEntry] = [
    WorkflowCatalogEntry(
        workflow_type="feature",
        description="End-to-end feature delivery pipeline",
        stages=["spec", "design", "implement", "review", "test", "deploy"],
    ),
    WorkflowCatalogEntry(
        workflow_type="bugfix",
        description="Bug triage, fix, and verification",
        stages=["triage", "fix", "review", "test", "deploy"],
    ),
]


@router.post("/start", response_model=WorkflowRunRead, status_code=201)
async def start_workflow(body: WorkflowRunCreate, db: AsyncSession = Depends(get_db)):
    run = await svc.create_workflow_run(db, body)
    try:
        await svc.start_temporal_workflow(db, run, config=body.config)
    except Exception:
        logger.warning("Temporal unavailable — workflow %s created without orchestration", run.id)
    return run


@router.get("/", response_model=WorkflowRunList)
async def list_workflows(
    status: str | None = Query(None),
    workflow_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await svc.list_workflow_runs(db, status=status, workflow_type=workflow_type, limit=limit, offset=offset)
    return WorkflowRunList(items=[WorkflowRunRead.model_validate(i) for i in items], total=total)


@router.get("/catalog", response_model=list[WorkflowCatalogEntry])
async def get_catalog():
    return WORKFLOW_CATALOG


@router.get("/{run_id}", response_model=WorkflowRunRead)
async def get_workflow(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    run = await svc.get_workflow_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return run


@router.post("/{run_id}/signal", status_code=204)
async def signal_workflow(run_id: uuid.UUID, body: WorkflowSignal, db: AsyncSession = Depends(get_db)):
    run = await svc.get_workflow_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    if not run.temporal_run_id:
        raise HTTPException(status_code=400, detail="Workflow has no Temporal run")
    workflow_id = f"pz-{run.workflow_type}-{run.id}"
    await temporal.signal_workflow(workflow_id, body.signal_name, body.payload)


@router.get("/{run_id}/steps", response_model=list[WorkflowStepRead])
async def get_workflow_steps(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    steps = await svc.get_steps_for_run(db, run_id)
    return [WorkflowStepRead.model_validate(s) for s in steps]


class StageGateStatus(BaseModel):
    current_stage: str | None
    next_stage: str | None
    can_advance: bool
    blocking_reason: str | None


@router.get("/{run_id}/stage-gate", response_model=StageGateStatus)
async def get_stage_gate(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Return current stage, next stage, and whether workflow can advance."""
    run = await svc.get_workflow_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    current = run.current_stage
    nxt = _next_stage(current) if current else STAGE_ORDER[0]

    blocking_reason: str | None = None
    can_advance = True

    if is_terminal(current or ""):
        can_advance = False
        blocking_reason = f"Workflow is in terminal state '{current}'"
    elif run.status == "failed":
        can_advance = False
        blocking_reason = "Workflow has failed — resolve failure before advancing"
    elif run.status == "blocked":
        can_advance = False
        blocking_reason = "Workflow is blocked — pending approval or manual intervention"
    elif current == "completion":
        can_advance = False
        blocking_reason = "Already at final stage"
        nxt = None

    return StageGateStatus(
        current_stage=current,
        next_stage=nxt,
        can_advance=can_advance,
        blocking_reason=blocking_reason,
    )
