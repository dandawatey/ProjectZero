from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workflow import (
    WorkflowTriggerCreate,
    WorkflowTriggerUpdate,
    WorkflowTriggerRead,
)
from app.services import workflow_service as svc

router = APIRouter()


@router.post("/", response_model=WorkflowTriggerRead, status_code=201)
async def create_trigger(body: WorkflowTriggerCreate, db: AsyncSession = Depends(get_db)):
    trigger = await svc.create_trigger(db, body)
    return WorkflowTriggerRead.model_validate(trigger)


@router.get("/", response_model=list[WorkflowTriggerRead])
async def list_triggers(db: AsyncSession = Depends(get_db)):
    triggers = await svc.list_triggers(db)
    return [WorkflowTriggerRead.model_validate(t) for t in triggers]


@router.put("/{trigger_id}", response_model=WorkflowTriggerRead)
async def update_trigger(
    trigger_id: uuid.UUID,
    body: WorkflowTriggerUpdate,
    db: AsyncSession = Depends(get_db),
):
    trigger = await svc.update_trigger(db, trigger_id, body)
    if trigger is None:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return WorkflowTriggerRead.model_validate(trigger)


@router.delete("/{trigger_id}", status_code=204)
async def delete_trigger(trigger_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await svc.delete_trigger(db, trigger_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trigger not found")
