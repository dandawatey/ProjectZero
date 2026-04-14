"""Agent routes — PRJ0-49 catalog + contributions, status, per-agent work history."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.workflow import AgentContribution, WorkflowStep, WorkflowRun
from app.models.agent import Agent
from app.schemas.agent import AgentRead, AgentCreate, AgentUpdate

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


# ---------------------------------------------------------------------------
# PRJ0-49 — Agent Catalog CRUD
# ---------------------------------------------------------------------------

SKILL_CATALOG = [
    {"id": "spec", "name": "Specification", "description": "Parse PRDs, generate user stories, acceptance criteria"},
    {"id": "arch", "name": "Architecture", "description": "Design systems, write ADRs, define API contracts"},
    {"id": "implement", "name": "Implementation", "description": "TDD cycles, write code, run quality gates"},
    {"id": "review", "name": "Review", "description": "Code review, quality-gate enforcement, PR analysis"},
    {"id": "deploy", "name": "Deploy", "description": "Release tagging, changelog generation, stakeholder notification"},
]


def _agent_to_read(a: Agent) -> AgentRead:
    return AgentRead(
        id=str(a.id),
        agent_id=a.agent_id,
        name=a.name,
        skills=a.skills or [],
        model=a.model,
        status=a.status,
        prompt_template_key=a.prompt_template_key,
        last_used_at=a.last_used_at.isoformat() if a.last_used_at else None,
        created_at=a.created_at.isoformat(),
    )


@router.get("", response_model=list[AgentRead])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """List all registered agents."""
    result = await db.execute(select(Agent).order_by(Agent.created_at))
    return [_agent_to_read(a) for a in result.scalars().all()]


@router.get("/skills")
async def list_skills():
    """Return static skill catalog."""
    return SKILL_CATALOG


@router.post("", response_model=AgentRead, status_code=201)
async def create_agent(payload: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Register a new agent."""
    existing = await db.execute(select(Agent).where(Agent.agent_id == payload.agent_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Agent '{payload.agent_id}' already exists")
    agent = Agent(**payload.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return _agent_to_read(agent)


@router.get("/executions")
async def list_executions(
    agent_id: str | None = None,
    skill_id: str | None = None,
    ticket_id: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List agent execution logs — PRJ0-53."""
    from app.models.agent_execution import AgentExecution
    q = select(AgentExecution).order_by(AgentExecution.started_at.desc()).limit(min(limit, 200))
    if agent_id:
        q = q.where(AgentExecution.agent_id == agent_id)
    if skill_id:
        q = q.where(AgentExecution.skill_id == skill_id)
    if ticket_id:
        q = q.where(AgentExecution.ticket_id == ticket_id)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "agent_id": r.agent_id,
            "skill_id": r.skill_id,
            "ticket_id": r.ticket_id,
            "workflow_run_id": r.workflow_run_id,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "duration_ms": r.duration_ms,
            "status": r.status,
            "quality_gate_passed": r.quality_gate_passed,
            "brain_written": r.brain_written,
            "error_message": r.error_message,
        }
        for r in rows
    ]


@router.patch("/{agent_id}", response_model=AgentRead)
async def update_agent(agent_id: str, payload: AgentUpdate, db: AsyncSession = Depends(get_db)):
    """Update agent status and/or model."""
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    updates = payload.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(agent, field, value)
    await db.commit()
    await db.refresh(agent)
    return _agent_to_read(agent)
