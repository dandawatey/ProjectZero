from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workflow import WorkflowArtifactCreate, WorkflowArtifactRead
from app.services import workflow_service as svc

router = APIRouter()


@router.post("/", response_model=WorkflowArtifactRead, status_code=201)
async def create_artifact(body: WorkflowArtifactCreate, db: AsyncSession = Depends(get_db)):
    artifact = await svc.create_artifact(db, body)
    return WorkflowArtifactRead.model_validate(artifact)


@router.get("/{workflow_run_id}", response_model=list[WorkflowArtifactRead])
async def get_artifacts(workflow_run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    artifacts = await svc.get_artifacts_for_run(db, workflow_run_id)
    return [WorkflowArtifactRead.model_validate(a) for a in artifacts]
