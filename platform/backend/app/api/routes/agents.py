"""Agent routes — contributions, status, per-agent work history."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.workflow import AgentContribution, WorkflowStep, WorkflowRun

router = APIRouter()


@router.get("/contributions/{workflow_run_id}")
async def get_contributions(workflow_run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AgentContribution)
        .where(AgentContribution.workflow_run_id == workflow_run_id)
        .order_by(desc(AgentContribution.created_at))
    )
    contribs = result.scalars().all()
    return [
        {"id": str(c.id), "agent_type": c.agent_type, "agent_id": c.agent_id,
         "action": c.action, "result": c.result, "duration_ms": c.duration_ms,
         "created_at": c.created_at.isoformat() if c.created_at else None}
        for c in contribs
    ]


@router.get("/status")
async def agent_status(db: AsyncSession = Depends(get_db)):
    """All agent types and their current status."""
    active = await db.execute(
        select(WorkflowStep.agent_type, WorkflowStep.stage_name, WorkflowStep.workflow_run_id)
        .where(WorkflowStep.status == "in_progress")
    )
    active_list = active.all()
    return {
        "active": [
            {"agent_type": r[0], "stage": r[1], "workflow_run_id": str(r[2])}
            for r in active_list
        ],
        "count": len(active_list),
    }


@router.get("/work/{agent_type}")
async def agent_work(agent_type: str, db: AsyncSession = Depends(get_db)):
    """Full work profile for an agent: current, pending, completed."""

    # Current (in_progress steps assigned to this agent)
    current_q = await db.execute(
        select(WorkflowStep)
        .where(and_(WorkflowStep.agent_type == agent_type, WorkflowStep.status == "in_progress"))
    )
    current_steps = current_q.scalars().all()
    current = []
    for s in current_steps:
        wf = await db.get(WorkflowRun, s.workflow_run_id)
        current.append({
            "feature_id": wf.feature_id if wf else "unknown",
            "stage": s.stage_name,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "workflow_run_id": str(s.workflow_run_id),
        })

    # Pending (ready steps that will be assigned to this agent type)
    pending_q = await db.execute(
        select(WorkflowStep)
        .where(and_(WorkflowStep.agent_type == agent_type, WorkflowStep.status == "pending"))
        .order_by(WorkflowStep.started_at)
    )
    pending_steps = pending_q.scalars().all()
    pending = []
    for s in pending_steps:
        wf = await db.get(WorkflowRun, s.workflow_run_id)
        pending.append({
            "feature_id": wf.feature_id if wf else "unknown",
            "stage": s.stage_name,
            "status": s.status,
            "priority": "P2",  # from workflow context
            "workflow_run_id": str(s.workflow_run_id),
        })

    # Completed contributions
    completed_q = await db.execute(
        select(AgentContribution)
        .where(AgentContribution.agent_type == agent_type)
        .order_by(desc(AgentContribution.created_at))
        .limit(50)
    )
    completed_contribs = completed_q.scalars().all()
    completed = []
    for c in completed_contribs:
        wf = await db.get(WorkflowRun, c.workflow_run_id)
        completed.append({
            "feature_id": wf.feature_id if wf else "unknown",
            "action": c.action,
            "result": c.result,
            "duration_ms": c.duration_ms,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {
        "agent_type": agent_type,
        "current": current,
        "pending": pending,
        "completed": completed,
    }
