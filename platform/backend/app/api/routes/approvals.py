from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workflow import (
    WorkflowApprovalCreate,
    WorkflowApprovalRead,
    ApprovalResolve,
)
from app.services import workflow_service as svc

router = APIRouter()


@router.get("/pending", response_model=list[WorkflowApprovalRead])
async def list_pending(db: AsyncSession = Depends(get_db)):
    approvals = await svc.list_pending_approvals(db)
    return [WorkflowApprovalRead.model_validate(a) for a in approvals]


@router.post("/{approval_id}/resolve", response_model=WorkflowApprovalRead)
async def resolve_approval(
    approval_id: uuid.UUID,
    body: ApprovalResolve,
    db: AsyncSession = Depends(get_db),
):
    approval = await svc.resolve_approval(db, approval_id, body)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return WorkflowApprovalRead.model_validate(approval)


@router.get("/{workflow_run_id}", response_model=list[WorkflowApprovalRead])
async def get_approvals(workflow_run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    approvals = await svc.get_approvals_for_run(db, workflow_run_id)
    return [WorkflowApprovalRead.model_validate(a) for a in approvals]
