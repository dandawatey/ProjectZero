from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workflow import StepSyncRequest, WorkflowStepRead
from app.services import workflow_service as svc

router = APIRouter()


@router.post("/sync", response_model=WorkflowStepRead, status_code=200)
async def sync_step(body: StepSyncRequest, db: AsyncSession = Depends(get_db)):
    """Idempotent step recording — safe to call multiple times with the same correlation_id."""
    try:
        step = await svc.record_step(db, body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return WorkflowStepRead.model_validate(step)


@router.get("/{workflow_run_id}", response_model=list[WorkflowStepRead])
async def get_steps(workflow_run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    steps = await svc.get_steps_for_run(db, workflow_run_id)
    return [WorkflowStepRead.model_validate(s) for s in steps]
