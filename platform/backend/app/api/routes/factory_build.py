"""Factory self-build endpoints — dogfood pipeline for PRJ0 tickets.

POST /factory-build
    Start FactorySelfBuildWorkflow for a PRJ0 ticket.

POST /factory-build/webhook/jira
    JIRA webhook receiver — auto-starts workflow when PRJ0 ticket moves to
    "In Progress". Idempotent: no duplicate workflows per ticket.
"""

from __future__ import annotations

import logging
import os
import uuid as _uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.workflow import WorkflowRun
from app.temporal_integration import client as temporal
from app.temporal_integration.workflows import WorkflowInput

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Factory repo root detection
# ---------------------------------------------------------------------------

def _factory_repo_path() -> str:
    """Return factory repo root from env or by walking up from this file."""
    env_path = os.getenv("FACTORY_REPO_PATH", "")
    if env_path:
        return env_path
    # Walk up: this file lives at platform/backend/app/api/routes/factory_build.py
    # repo root is 5 levels up
    here = Path(__file__).resolve()
    return str(here.parents[5])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class FactoryBuildRequest(BaseModel):
    jira_ticket_id: str  # e.g. "PRJ0-55"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _start_factory_workflow(
    jira_ticket_id: str,
    db: AsyncSession,
) -> dict:
    """Create WorkflowRun + start FactorySelfBuildWorkflow. Returns run metadata."""
    run_id = _uuid.uuid4()
    repo_path = _factory_repo_path()

    run = WorkflowRun(
        id=run_id,
        workflow_type="factory",
        feature_id=jira_ticket_id,
        product_id="ProjectZeroFactory",
        status="running",
        current_stage="specification",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    wf_id = f"factory-{jira_ticket_id}-{run_id}"
    wf_input = WorkflowInput(
        workflow_run_id=str(run_id),
        product_id="ProjectZeroFactory",
        product_name="ProjectZeroFactory",
        repo_path=repo_path,
        jira_project_key="PRJ0",
        feature_id=jira_ticket_id,
    )

    try:
        temporal_run_id = await temporal.start_workflow(
            "FactorySelfBuildWorkflow",
            workflow_id=wf_id,
            args=[wf_input],
        )
        run.temporal_run_id = temporal_run_id
        await db.commit()
        logger.info(
            "FactorySelfBuildWorkflow started — ticket=%s wf_id=%s run_id=%s",
            jira_ticket_id, wf_id, temporal_run_id,
        )
        return {
            "workflow_run_id": str(run_id),
            "temporal_run_id": temporal_run_id,
            "temporal_workflow_id": wf_id,
            "jira_ticket_id": jira_ticket_id,
            "repo_path": repo_path,
            "stage": "specification",
            "status": "running",
        }
    except Exception as exc:
        # Temporal not available — queue as pending, can retry
        run.status = "pending"
        await db.commit()
        logger.warning("Temporal unavailable for factory workflow: %s", exc)
        return {
            "workflow_run_id": str(run_id),
            "temporal_run_id": None,
            "jira_ticket_id": jira_ticket_id,
            "repo_path": repo_path,
            "warning": f"Temporal unavailable — workflow queued: {exc}",
        }


async def _workflow_already_running(jira_ticket_id: str, db: AsyncSession) -> bool:
    """Return True if an active factory workflow exists for this ticket."""
    result = await db.execute(
        select(WorkflowRun).where(
            WorkflowRun.workflow_type == "factory",
            WorkflowRun.feature_id == jira_ticket_id,
            WorkflowRun.status == "running",
        )
    )
    return result.scalar_one_or_none() is not None


# ---------------------------------------------------------------------------
# POST /factory-build — manual trigger
# ---------------------------------------------------------------------------

@router.post("", status_code=202)
async def start_factory_build(
    req: FactoryBuildRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Start FactorySelfBuildWorkflow for a PRJ0 ticket.

    Body: {"jira_ticket_id": "PRJ0-55"}

    Creates WorkflowRun in DB, starts Temporal workflow.
    Returns workflow_run_id + temporal_run_id.
    """
    ticket = req.jira_ticket_id.strip().upper()
    if not ticket.startswith("PRJ0-"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticket ID '{ticket}' — must be a PRJ0 ticket (e.g. PRJ0-55)",
        )

    if await _workflow_already_running(ticket, db):
        raise HTTPException(
            status_code=409,
            detail=f"FactorySelfBuildWorkflow already running for {ticket}",
        )

    return await _start_factory_workflow(ticket, db)


# ---------------------------------------------------------------------------
# POST /factory-build/webhook/jira — JIRA webhook receiver
# ---------------------------------------------------------------------------

@router.post("/webhook/jira", status_code=200)
async def jira_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    JIRA webhook receiver. Auto-starts FactorySelfBuildWorkflow when a PRJ0
    issue transitions to "In Progress".

    Always returns 200 — JIRA requires a fast response.
    Errors are logged, not raised (JIRA will retry on non-200).

    Expected payload (JIRA issue:updated event):
    {
      "webhookEvent": "jira:issue_updated",
      "issue": {
        "key": "PRJ0-55",
        "fields": {
          "project": {"key": "PRJ0"},
          "status": {"name": "In Progress"}
        }
      }
    }
    """
    try:
        payload = await request.json()
    except Exception as exc:
        logger.warning("JIRA webhook: failed to parse JSON body: %s", exc)
        return {"received": True, "action": "ignored", "reason": "invalid JSON"}

    # Extract issue info
    issue = payload.get("issue", {})
    fields = issue.get("fields", {})
    project_key = fields.get("project", {}).get("key", "")
    status_name = fields.get("status", {}).get("name", "")
    ticket_key = issue.get("key", "")

    # Only act on PRJ0 tickets moving to "In Progress"
    if project_key != "PRJ0":
        return {"received": True, "action": "ignored", "reason": f"project={project_key} (not PRJ0)"}

    if status_name != "In Progress":
        return {"received": True, "action": "ignored", "reason": f"status='{status_name}' (not In Progress)"}

    if not ticket_key:
        return {"received": True, "action": "ignored", "reason": "no issue key in payload"}

    # Idempotent: skip if workflow already running for this ticket
    try:
        already = await _workflow_already_running(ticket_key, db)
    except Exception as exc:
        logger.error("JIRA webhook: DB check failed for %s: %s", ticket_key, exc)
        return {"received": True, "action": "error", "reason": str(exc)}

    if already:
        logger.info("JIRA webhook: workflow already running for %s — skipping", ticket_key)
        return {"received": True, "action": "skipped", "reason": "workflow already running", "ticket": ticket_key}

    # Start workflow (non-blocking: errors are logged, not raised)
    try:
        result = await _start_factory_workflow(ticket_key, db)
        logger.info("JIRA webhook: started FactorySelfBuildWorkflow for %s", ticket_key)
        return {"received": True, "action": "started", "ticket": ticket_key, "workflow_run_id": result["workflow_run_id"]}
    except Exception as exc:
        logger.error("JIRA webhook: failed to start workflow for %s: %s", ticket_key, exc)
        return {"received": True, "action": "error", "reason": str(exc), "ticket": ticket_key}
