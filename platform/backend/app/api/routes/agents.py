from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workflow import AgentContributionRead
from app.services import workflow_service as svc

router = APIRouter()


@router.get("/contributions/{workflow_run_id}", response_model=list[AgentContributionRead])
async def get_contributions(workflow_run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    contribs = await svc.get_contributions_for_run(db, workflow_run_id)
    return [AgentContributionRead.model_validate(c) for c in contribs]


@router.get("/status")
async def agent_status():
    """Lightweight probe — extend with real agent-pool health checks."""
    return {"status": "ok", "agents": []}
