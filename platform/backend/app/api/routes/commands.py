"""Factory command endpoints — PRJ0-46.

POST /api/v1/commands/spec    → trigger FeatureDevelopmentWorkflow (stage=specification)
POST /api/v1/commands/approve → send approve_stage signal to running workflow
POST /api/v1/commands/reject  → send reject signal to running workflow

These are the primary human↔factory interface endpoints.
"""

from __future__ import annotations

import uuid as _uuid
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.agent_resolver import STAGE_AGENT_MAP
from app.models.product import Product
from app.models.workflow import WorkflowRun
from app.temporal_integration import client as temporal
from app.temporal_integration.workflows import WorkflowInput, ApprovalSignal

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SpecRequest(BaseModel):
    product_id: str
    jira_feature_id: str    # e.g. "INETZERO-42"


class ApproveRequest(BaseModel):
    workflow_run_id: str
    stage: str              # specification | architecture | realization | completion
    approved: bool = True
    comment: str = ""


# ---------------------------------------------------------------------------
# /spec — start FeatureDevelopmentWorkflow
# ---------------------------------------------------------------------------

@router.post("/spec", status_code=202)
async def spec_command(req: SpecRequest, db: AsyncSession = Depends(get_db)):
    """
    Trigger FeatureDevelopmentWorkflow for a product+feature.
    Creates WorkflowRun record, starts Temporal workflow.
    Returns workflow_run_id + temporal_run_id.
    """
    # Validate product
    try:
        pid = _uuid.UUID(req.product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product_id")

    result = await db.execute(select(Product).where(Product.id == pid))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Create WorkflowRun
    run_id = _uuid.uuid4()
    run = WorkflowRun(
        id=run_id,
        workflow_type="feature",
        feature_id=req.jira_feature_id,
        product_id=str(pid),
        status="running",
        current_stage="specification",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Start Temporal workflow
    wf_id = f"feature-{req.jira_feature_id}-{run_id}"
    wf_input = WorkflowInput(
        workflow_run_id=str(run_id),
        product_id=str(pid),
        product_name=product.name,
        repo_path=product.repo_path,
        jira_project_key=product.jira_project_key or req.jira_feature_id.split("-")[0],
        feature_id=req.jira_feature_id,
    )

    try:
        temporal_run_id = await temporal.start_workflow(
            "FeatureDevelopmentWorkflow",
            workflow_id=wf_id,
            args=[wf_input],
        )
        run.temporal_run_id = temporal_run_id
        await db.commit()
    except Exception as exc:
        # Temporal not running — record as pending, can retry later
        run.status = "pending"
        run.current_stage = "specification"
        await db.commit()
        return {
            "workflow_run_id": str(run_id),
            "temporal_run_id": None,
            "warning": f"Temporal unavailable — workflow queued: {exc}",
        }

    return {
        "workflow_run_id": str(run_id),
        "temporal_run_id": temporal_run_id,
        "temporal_workflow_id": wf_id,
        "stage": "specification",
        "status": "running",
    }


# ---------------------------------------------------------------------------
# /approve — signal running workflow
# ---------------------------------------------------------------------------

@router.post("/approve", status_code=200)
async def approve_command(req: ApproveRequest, db: AsyncSession = Depends(get_db)):
    """Send approve_stage or reject_stage signal to a running workflow."""
    try:
        rid = _uuid.UUID(req.workflow_run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow_run_id")

    result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == rid))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="WorkflowRun not found")
    if not run.temporal_run_id:
        raise HTTPException(status_code=409, detail="Workflow has no Temporal run ID — not started yet")

    # Signal Temporal
    wf_id = f"feature-{run.feature_id}-{run.id}"
    sig = ApprovalSignal(stage=req.stage, approved=req.approved, comment=req.comment)
    try:
        await temporal.signal_workflow(wf_id, "approve_stage", sig)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Temporal signal failed: {exc}")

    # Update DB stage
    if req.approved:
        stage_order = ["specification", "architecture", "realization", "completion", "completed"]
        current_idx = stage_order.index(req.stage) if req.stage in stage_order else 0
        next_stage = stage_order[min(current_idx + 1, len(stage_order) - 1)]
        run.current_stage = next_stage
    else:
        run.status = "failed"
        run.current_stage = req.stage

    await db.commit()
    return {"signalled": True, "stage": req.stage, "approved": req.approved}


# ---------------------------------------------------------------------------
# /agent-map — expose STAGE_AGENT_MAP as JSON (PRJ0-39)
# ---------------------------------------------------------------------------

@router.get("/agent-map", status_code=200)
async def agent_map():
    """Return full STAGE_AGENT_MAP: stage → [{activity, agent_type, task_queue, description}]."""
    return {
        "stages": STAGE_AGENT_MAP,
        "stage_order": list(STAGE_AGENT_MAP.keys()),
    }
