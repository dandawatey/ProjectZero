"""Factory command endpoints — PRJ0-46.

POST /api/v1/commands/spec    → trigger FeatureDevelopmentWorkflow (stage=specification)
POST /api/v1/commands/approve → send approve_stage signal to running workflow
POST /api/v1/commands/reject  → send reject signal to running workflow

These are the primary human↔factory interface endpoints.
"""

from __future__ import annotations

import uuid as _uuid
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import Product
from app.models.workflow import WorkflowRun
from app.services.spec_parser import parse_prd_to_stories
from app.temporal_integration import client as temporal
from app.temporal_integration.workflows import WorkflowInput, ApprovalSignal

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SpecRequest(BaseModel):
    product_id: str
    jira_feature_id: str    # e.g. "INETZERO-42"


class SpecParseRequest(BaseModel):
    product_id: str
    prd_text: str               # Raw PRD / feature description
    jira_project_key: str
    create_jira_tickets: bool = True  # If True, create JIRA tickets via JiraClient


class ApproveRequest(BaseModel):
    workflow_run_id: str
    stage: str              # specification | architecture | realization | completion
    approved: bool = True
    comment: str = ""


# ---------------------------------------------------------------------------
# /spec — start FeatureDevelopmentWorkflow
# ---------------------------------------------------------------------------

@router.post("/spec", status_code=202)
async def spec_command(req: SpecRequest, db: AsyncSession = Depends(get_db)):
    """
    Trigger FeatureDevelopmentWorkflow for a product+feature.
    Creates WorkflowRun record, starts Temporal workflow.
    Returns workflow_run_id + temporal_run_id.
    """
    # Validate product
    try:
        pid = _uuid.UUID(req.product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product_id")

    result = await db.execute(select(Product).where(Product.id == pid))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Create WorkflowRun
    run_id = _uuid.uuid4()
    run = WorkflowRun(
        id=run_id,
        workflow_type="feature",
        feature_id=req.jira_feature_id,
        product_id=str(pid),
        status="running",
        current_stage="specification",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Start Temporal workflow
    wf_id = f"feature-{req.jira_feature_id}-{run_id}"
    wf_input = WorkflowInput(
        workflow_run_id=str(run_id),
        product_id=str(pid),
        product_name=product.name,
        repo_path=product.repo_path,
        jira_project_key=product.jira_project_key or req.jira_feature_id.split("-")[0],
        feature_id=req.jira_feature_id,
    )

    try:
        temporal_run_id = await temporal.start_workflow(
            "FeatureDevelopmentWorkflow",
            workflow_id=wf_id,
            args=[wf_input],
        )
        run.temporal_run_id = temporal_run_id
        await db.commit()
    except Exception as exc:
        # Temporal not running — record as pending, can retry later
        run.status = "pending"
        run.current_stage = "specification"
        await db.commit()
        return {
            "workflow_run_id": str(run_id),
            "temporal_run_id": None,
            "warning": f"Temporal unavailable — workflow queued: {exc}",
        }

    return {
        "workflow_run_id": str(run_id),
        "temporal_run_id": temporal_run_id,
        "temporal_workflow_id": wf_id,
        "stage": "specification",
        "status": "running",
    }


# ---------------------------------------------------------------------------
# /spec/parse — synchronous PRD → stories (+ optional JIRA ticket creation)
# ---------------------------------------------------------------------------

@router.post("/spec/parse", status_code=200)
async def spec_parse(req: SpecParseRequest, db: AsyncSession = Depends(get_db)):
    """Synchronously parse PRD text → user stories. Optionally create JIRA tickets."""
    from dataclasses import asdict
    from app.services.jira_client import JiraClient

    # 1. Parse PRD via Claude
    try:
        spec = await parse_prd_to_stories(req.prd_text, req.jira_project_key)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Claude parse failed: {exc}")

    # 2. Optionally create JIRA tickets
    jira_keys: list[str] = []
    jira_errors: list[str] = []

    if req.create_jira_tickets:
        try:
            jira = JiraClient()
            priority_map = {1: "Highest", 2: "High", 3: "Medium", 4: "Low", 5: "Lowest"}
            for story in spec.stories:
                ac_text = "\n".join(
                    f"Given {ac.given}\nWhen {ac.when}\nThen {ac.then}"
                    for ac in story.acceptance_criteria
                )
                description = (
                    f"As a {story.role}, I want to {story.action}, so that {story.benefit}.\n\n"
                    f"Acceptance Criteria:\n{ac_text}"
                )
                try:
                    result = await jira.create_issue(
                        project_key=req.jira_project_key,
                        summary=story.title,
                        description=description,
                        issue_type="Story",
                        priority=priority_map.get(story.priority, "Medium"),
                        story_points=story.estimate_sp,
                        labels=["spec-agent", "PRJ0-40"],
                    )
                    jira_keys.append(result.get("key", ""))
                except Exception as exc:
                    jira_errors.append(f"{story.title}: {exc}")
        except RuntimeError as exc:
            # JIRA not configured — skip silently, report in response
            jira_errors.append(f"JIRA not configured: {exc}")

    # 3. Serialize SpecResult → dict
    def _criterion_dict(ac):
        return {"given": ac.given, "when": ac.when, "then": ac.then}

    def _story_dict(s):
        return {
            "title": s.title,
            "role": s.role,
            "action": s.action,
            "benefit": s.benefit,
            "priority": s.priority,
            "estimate_sp": s.estimate_sp,
            "acceptance_criteria": [_criterion_dict(ac) for ac in s.acceptance_criteria],
        }

    return {
        "feature_title": spec.feature_title,
        "feature_summary": spec.feature_summary,
        "risks": spec.risks,
        "dependencies": spec.dependencies,
        "stories": [_story_dict(s) for s in spec.stories],
        "jira_tickets_created": jira_keys,
        "jira_errors": jira_errors,
    }


# ---------------------------------------------------------------------------
# /approve — signal running workflow
# ---------------------------------------------------------------------------

@router.post("/approve", status_code=200)
async def approve_command(req: ApproveRequest, db: AsyncSession = Depends(get_db)):
    """Send approve_stage or reject_stage signal to a running workflow."""
    try:
        rid = _uuid.UUID(req.workflow_run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow_run_id")

    result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == rid))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="WorkflowRun not found")
    if not run.temporal_run_id:
        raise HTTPException(status_code=409, detail="Workflow has no Temporal run ID — not started yet")

    # Signal Temporal
    wf_id = f"feature-{run.feature_id}-{run.id}"
    sig = ApprovalSignal(stage=req.stage, approved=req.approved, comment=req.comment)
    try:
        await temporal.signal_workflow(wf_id, "approve_stage", sig)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Temporal signal failed: {exc}")

    # Update DB stage
    if req.approved:
        stage_order = ["specification", "architecture", "realization", "completion", "completed"]
        current_idx = stage_order.index(req.stage) if req.stage in stage_order else 0
        next_stage = stage_order[min(current_idx + 1, len(stage_order) - 1)]
        run.current_stage = next_stage
    else:
        run.status = "failed"
        run.current_stage = req.stage

    await db.commit()
    return {"signalled": True, "stage": req.stage, "approved": req.approved}
