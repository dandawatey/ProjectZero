"""Unified ticket submission endpoint.

POST /api/v1/tickets/submit  — classify + route any ticket to correct Temporal workflow
GET  /api/v1/tickets/{workflow_run_id}/status  — classification + current stage
POST /api/v1/tickets/{workflow_run_id}/approve — approve a stage gate
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


class TicketSubmitRequest(BaseModel):
    ticket_id: str                          # e.g. PRJ0-47 or PROJ-123
    ticket_type: str = "Story"              # Epic | Story | Bug | Task | Sub-task
    title: str
    description: str = ""
    product_id: str
    product_name: str
    repo_path: str = "/tmp/pzero-artifacts"
    jira_project_key: str = "PRJ0"
    child_ticket_ids: list[str] = []        # for Epics: list of child story IDs


class ApproveStageRequest(BaseModel):
    stage: str
    approved: bool
    comment: str = ""


@router.post("/submit", status_code=202)
async def submit_ticket(body: TicketSubmitRequest, db: AsyncSession = Depends(get_db)):
    """
    Classify a ticket and start the correct Temporal workflow.

    Routing:
      Epic      → EpicOrchestratorWorkflow  (spawns child StoryWorkflows)
      Story     → FeatureDevelopmentWorkflow (Spec→Arch→Impl→Review→Deploy, 3 gates)
      Bug/high  → BugFixWorkflow             (Diagnose→Fix→Verify, 1 gate)
      Bug/low   → BugFixWorkflow             (auto-approve, no gates)
      Task      → TaskWorkflow               (Impl→Review, fully automated)
    """
    from app.temporal_integration import client as temporal
    from app.temporal_integration.ticket_router_workflow import (
        TicketRouterWorkflow,
        TicketRouterInput,
    )
    from app.models.workflow import WorkflowRun
    from app.services.workflow_service import create_workflow_run
    from app.schemas.workflow import WorkflowRunCreate

    # Create DB record
    run_id = str(uuid.uuid4())
    wf_create = WorkflowRunCreate(
        workflow_type=f"ticket_router_{body.ticket_type.lower()}",
        feature_id=body.ticket_id,
        product_id=body.product_id,
    )
    wf_run = await create_workflow_run(db, wf_create)
    run_id = str(wf_run.id)

    # Start Temporal workflow
    try:
        temporal_run_id = await temporal.start_workflow(
            "TicketRouterWorkflow",
            workflow_id=f"ticket-{body.ticket_id}-{run_id[:8]}",
            args=[
                TicketRouterInput(
                    workflow_run_id=run_id,
                    product_id=body.product_id,
                    product_name=body.product_name,
                    repo_path=body.repo_path,
                    jira_project_key=body.jira_project_key,
                    ticket_id=body.ticket_id,
                    ticket_type=body.ticket_type,
                    title=body.title,
                    description=body.description,
                    child_ticket_ids=body.child_ticket_ids,
                )
            ],
        )
    except Exception as exc:
        logger.error("Failed to start TicketRouterWorkflow: %s", exc)
        raise HTTPException(status_code=503, detail=f"Temporal unavailable: {exc}")

    return {
        "workflow_run_id": run_id,
        "ticket_id": body.ticket_id,
        "ticket_type": body.ticket_type,
        "temporal_workflow_id": f"ticket-{body.ticket_id}-{run_id[:8]}",
        "status": "started",
        "message": f"Ticket {body.ticket_id} submitted — classifier will route to correct workflow",
        "temporal_ui": f"http://localhost:8233/namespaces/default/workflows/ticket-{body.ticket_id}-{run_id[:8]}",
    }


@router.get("/{workflow_run_id}/status")
async def ticket_status(workflow_run_id: str):
    """Query current stage + classification of a ticket workflow."""
    from app.temporal_integration import client as temporal

    try:
        client = await temporal.get_temporal_client()
        # Find the workflow by run_id prefix
        handle = client.get_workflow_handle(f"ticket-router-{workflow_run_id[:8]}")
        stage = await handle.query("current_stage")
        clf = await handle.query("classification")
        return {
            "workflow_run_id": workflow_run_id,
            "current_stage": stage,
            "classification": clf,
        }
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {exc}")


@router.post("/{temporal_workflow_id}/approve")
async def approve_ticket_stage(temporal_workflow_id: str, body: ApproveStageRequest):
    """
    Send approval signal to a running ticket workflow.
    The router proxies it to the correct child workflow automatically.
    """
    from app.temporal_integration import client as temporal
    from app.temporal_integration.workflows import ApprovalSignal

    try:
        await temporal.signal_workflow(
            temporal_workflow_id,
            "approve_stage",
            ApprovalSignal(
                stage=body.stage,
                approved=body.approved,
                comment=body.comment,
            ),
        )
        return {
            "signalled": True,
            "workflow_id": temporal_workflow_id,
            "stage": body.stage,
            "approved": body.approved,
        }
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Could not signal workflow: {exc}")
