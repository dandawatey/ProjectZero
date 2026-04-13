from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workflow import WorkflowAuditCreate, WorkflowAuditRead
from app.services import workflow_service as svc

router = APIRouter()


@router.post("/", response_model=WorkflowAuditRead, status_code=201)
async def create_audit_entry(body: WorkflowAuditCreate, db: AsyncSession = Depends(get_db)):
    entry = await svc.create_audit_entry(db, body)
    return WorkflowAuditRead.model_validate(entry)


@router.get("/{workflow_run_id}", response_model=list[WorkflowAuditRead])
async def get_audit_for_run(workflow_run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    entries = await svc.get_audit_for_run(db, workflow_run_id)
    return [WorkflowAuditRead.model_validate(e) for e in entries]


@router.get("/", response_model=list[WorkflowAuditRead])
async def list_audit(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    entries = await svc.list_audit_entries(db, limit=limit, offset=offset)
    return [WorkflowAuditRead.model_validate(e) for e in entries]
