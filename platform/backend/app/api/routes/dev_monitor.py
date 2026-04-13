"""Developer monitor routes — real-time view of agent execution."""

import subprocess
import os
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.workflow import WorkflowRun, WorkflowStep, AgentContribution
from app.models.activity import UserActivity

router = APIRouter()


@router.get("/overview")
async def dev_overview(db: AsyncSession = Depends(get_db)):
    """Real-time developer overview: what's happening right now."""

    # Active workflows
    active_wfs = await db.execute(
        select(WorkflowRun).where(WorkflowRun.status == "running").order_by(desc(WorkflowRun.updated_at))
    )
    active_workflows = active_wfs.scalars().all()

    # Active steps (in_progress)
    active_steps = await db.execute(
        select(WorkflowStep).where(WorkflowStep.status == "in_progress").order_by(desc(WorkflowStep.started_at))
    )
    current_steps = active_steps.scalars().all()

    # Recent agent contributions (last hour)
    from datetime import datetime, timedelta
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_contribs = await db.execute(
        select(AgentContribution).where(AgentContribution.created_at >= hour_ago)
        .order_by(desc(AgentContribution.created_at)).limit(20)
    )
    contributions = recent_contribs.scalars().all()

    # Recent activities
    recent_acts = await db.execute(
        select(UserActivity).where(UserActivity.created_at >= hour_ago)
        .order_by(desc(UserActivity.created_at)).limit(20)
    )
    activities = recent_acts.scalars().all()

    return {
        "active_workflows": [
            {"id": str(w.id), "type": w.workflow_type, "feature_id": w.feature_id,
             "stage": w.current_stage, "product_id": w.product_id,
             "updated_at": w.updated_at.isoformat() if w.updated_at else None}
            for w in active_workflows
        ],
        "current_steps": [
            {"id": str(s.id), "workflow_run_id": str(s.workflow_run_id),
             "stage": s.stage_name, "agent_type": s.agent_type,
             "started_at": s.started_at.isoformat() if s.started_at else None}
            for s in current_steps
        ],
        "recent_contributions": [
            {"id": str(c.id), "agent_type": c.agent_type, "action": c.action,
             "result": c.result, "duration_ms": c.duration_ms,
             "created_at": c.created_at.isoformat() if c.created_at else None}
            for c in contributions
        ],
        "recent_activities": [
            {"user_id": a.user_id, "action": a.action, "category": a.category,
             "status": a.status, "created_at": a.created_at.isoformat()}
            for a in activities
        ],
    }


@router.get("/worktrees")
async def list_worktrees():
    """List active git worktrees and tmux sessions."""
    # Get worktrees
    product_path = os.getenv("PRODUCT_PATH", ".")
    wt_result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=product_path, capture_output=True, text=True,
    )

    worktrees = []
    current = {}
    for line in wt_result.stdout.split("\n"):
        if line.startswith("worktree "):
            if current and current.get("path"):
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "")
        elif line == "":
            if current and current.get("path"):
                worktrees.append(current)
            current = {}

    # Get tmux sessions
    tmux_result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}:#{session_activity}"],
        capture_output=True, text=True,
    )
    sessions = {}
    if tmux_result.returncode == 0:
        for line in tmux_result.stdout.strip().split("\n"):
            if ":" in line:
                name, activity = line.split(":", 1)
                sessions[name] = activity

    # Match worktrees to sessions
    for wt in worktrees:
        branch = wt.get("branch", "")
        feature_id = branch.replace("feature/", "")
        session_name = f"agent-{feature_id}"
        wt["feature_id"] = feature_id
        wt["tmux_session"] = session_name if session_name in sessions else None
        wt["tmux_active"] = session_name in sessions

    return {"worktrees": worktrees, "tmux_sessions": list(sessions.keys())}


@router.get("/tmux/{session_name}/output")
async def get_tmux_output(session_name: str, lines: int = Query(default=50, le=500)):
    """Capture recent output from a tmux session."""
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session_name, "-p", "-S", f"-{lines}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return {"error": f"Session {session_name} not found", "output": ""}
    return {"session": session_name, "output": result.stdout, "lines": lines}


@router.get("/agents/live")
async def live_agent_status(db: AsyncSession = Depends(get_db)):
    """Which agents are currently active, what they're working on."""
    active = await db.execute(
        select(WorkflowStep).where(WorkflowStep.status == "in_progress")
    )
    steps = active.scalars().all()

    agents = []
    for s in steps:
        agents.append({
            "agent_type": s.agent_type,
            "agent_id": s.agent_id,
            "working_on": s.stage_name,
            "workflow_run_id": str(s.workflow_run_id),
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "duration_seconds": (
                ((__import__("datetime").datetime.utcnow() - s.started_at).total_seconds()
                 if s.started_at else 0)
            ),
        })

    return {"active_agents": agents, "count": len(agents)}


@router.get("/stats")
async def dev_stats(db: AsyncSession = Depends(get_db)):
    """Developer productivity stats."""
    from datetime import datetime, timedelta
    day_ago = datetime.utcnow() - timedelta(days=1)
    week_ago = datetime.utcnow() - timedelta(days=7)

    # Workflows completed today
    today_completed = await db.scalar(
        select(func.count(WorkflowRun.id))
        .where(WorkflowRun.status == "completed", WorkflowRun.updated_at >= day_ago)
    )

    # Total agent contributions this week
    week_contribs = await db.scalar(
        select(func.count(AgentContribution.id))
        .where(AgentContribution.created_at >= week_ago)
    )

    # Avg step duration
    avg_duration = await db.scalar(
        select(func.avg(AgentContribution.duration_ms))
        .where(AgentContribution.created_at >= week_ago)
    )

    # Steps completed today
    steps_today = await db.scalar(
        select(func.count(WorkflowStep.id))
        .where(WorkflowStep.status == "completed", WorkflowStep.completed_at >= day_ago)
    )

    return {
        "workflows_completed_today": today_completed or 0,
        "agent_contributions_this_week": week_contribs or 0,
        "avg_step_duration_ms": round(avg_duration or 0),
        "steps_completed_today": steps_today or 0,
    }
