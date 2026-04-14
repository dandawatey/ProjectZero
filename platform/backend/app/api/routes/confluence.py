"""Confluence API routes.

Endpoints:
  GET  /confluence/health            — JIRA + Confluence circuit status
  POST /confluence/product/{name}/init  — Create full page hierarchy for a product
  POST /confluence/product/{name}/sync  — Sync all sections (overview, arch, workflows, artifacts, decisions)
  POST /confluence/product/{name}/overview      — Sync overview only
  POST /confluence/product/{name}/architecture  — Sync architecture only
  POST /confluence/product/{name}/workflows     — Sync workflow history only
  POST /confluence/product/{name}/artifacts     — Sync artifacts only
  POST /confluence/product/{name}/decisions     — Sync decisions only
  GET  /confluence/dashboard                    — Public management dashboard data (no JIRA creds in response)
"""

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.confluence_client import ConfluenceClient
from app.services.integration_health import health_registry

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_client() -> ConfluenceClient:
    try:
        return ConfluenceClient()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@router.get("/health")
async def integration_health():
    """Live circuit-breaker state for JIRA and Confluence."""
    jira = health_registry.get("JIRA")
    conf = health_registry.get("Confluence")
    return {
        "jira": jira.to_dict() if jira else {"name": "JIRA", "status": "not_started"},
        "confluence": conf.to_dict() if conf else {"name": "Confluence", "status": "not_started"},
        "all_healthy": health_registry.all_healthy(),
    }


# ---------------------------------------------------------------------------
# Product page management
# ---------------------------------------------------------------------------

@router.post("/product/{product_name}/init")
async def init_product_pages(product_name: str):
    """Create the full Confluence page hierarchy for a product."""
    client = _get_client()
    parent_title = os.getenv("CONFLUENCE_PARENT_PAGE_TITLE", "ProjectZero Products")
    page_ids = await client.ensure_product_pages(product_name, parent_title)
    return {"product": product_name, "pages_created": page_ids}


class SyncOverviewRequest(BaseModel):
    prd: dict[str, Any] | None = None
    bmad: dict[str, Any] | None = None


@router.post("/product/{product_name}/overview")
async def sync_overview(product_name: str, body: SyncOverviewRequest):
    client = _get_client()
    ok = await client.sync_overview(product_name, body.prd, body.bmad)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Overview page for '{product_name}' not found — run /init first")
    return {"synced": "overview", "product": product_name}


class SyncArchitectureRequest(BaseModel):
    adrs: list[dict[str, Any]] = []
    tech_stack: dict[str, Any] | None = None
    api_notes: str | None = None


@router.post("/product/{product_name}/architecture")
async def sync_architecture(product_name: str, body: SyncArchitectureRequest):
    client = _get_client()
    ok = await client.sync_architecture(product_name, body.adrs, body.tech_stack, body.api_notes)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Architecture page for '{product_name}' not found — run /init first")
    return {"synced": "architecture", "product": product_name}


class SyncWorkflowsRequest(BaseModel):
    workflows: list[dict[str, Any]] = []


@router.post("/product/{product_name}/workflows")
async def sync_workflow_history(product_name: str, body: SyncWorkflowsRequest):
    client = _get_client()
    ok = await client.sync_workflow_history(product_name, body.workflows)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Workflow History page for '{product_name}' not found")
    return {"synced": "workflow_history", "product": product_name}


class SyncArtifactsRequest(BaseModel):
    artifacts: list[dict[str, Any]] = []


@router.post("/product/{product_name}/artifacts")
async def sync_artifacts(product_name: str, body: SyncArtifactsRequest):
    client = _get_client()
    ok = await client.sync_artifacts(product_name, body.artifacts)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Artifacts page for '{product_name}' not found")
    return {"synced": "artifacts", "product": product_name}


class SyncDecisionsRequest(BaseModel):
    decisions: list[dict[str, Any]] = []


@router.post("/product/{product_name}/decisions")
async def sync_decisions(product_name: str, body: SyncDecisionsRequest):
    client = _get_client()
    ok = await client.sync_decisions(product_name, body.decisions)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Decisions page for '{product_name}' not found")
    return {"synced": "decisions", "product": product_name}


class FullSyncRequest(BaseModel):
    prd: dict[str, Any] | None = None
    bmad: dict[str, Any] | None = None
    adrs: list[dict[str, Any]] = []
    tech_stack: dict[str, Any] | None = None
    workflows: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []


@router.post("/product/{product_name}/sync")
async def full_sync(product_name: str, body: FullSyncRequest):
    """Sync all sections for a product in one call. Creates pages if missing."""
    client = _get_client()
    parent_title = os.getenv("CONFLUENCE_PARENT_PAGE_TITLE", "ProjectZero Products")
    results = await client.sync_all(
        product_name=product_name,
        parent_title=parent_title,
        prd=body.prd,
        bmad=body.bmad,
        adrs=body.adrs,
        tech_stack=body.tech_stack,
        workflows=body.workflows,
        artifacts=body.artifacts,
        decisions=body.decisions,
    )
    return {"product": product_name, "sections_synced": results}


# ---------------------------------------------------------------------------
# Public management dashboard
# ---------------------------------------------------------------------------

@router.get("/dashboard")
async def management_dashboard():
    """
    Public management dashboard — aggregates data from our own DB/Brain only.
    No JIRA credentials included in response. Safe to share.

    Returns: integration health, products list with workflow summary.
    """
    from app.core.database import async_session as AsyncSessionLocal
    from sqlalchemy import select, func, text
    from app.models.workflow import WorkflowRun, WorkflowStep, WorkflowApproval, WorkflowArtifact
    from app.models.brain import Decision, Memory

    dashboard: dict[str, Any] = {
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "integration_health": {},
        "factory_summary": {},
        "products": [],
        "recent_activity": [],
    }

    # Integration health (status only — no tokens/URLs)
    jira_h = health_registry.get("JIRA")
    conf_h = health_registry.get("Confluence")
    dashboard["integration_health"] = {
        "jira": {
            "status": jira_h.status if jira_h else "unknown",
            "circuit": jira_h.circuit.state.value if jira_h else "unknown",
        },
        "confluence": {
            "status": conf_h.status if conf_h else "unknown",
            "circuit": conf_h.circuit.state.value if conf_h else "unknown",
        },
    }

    try:
        async with AsyncSessionLocal() as session:
            # Factory-level counts
            total_wf = (await session.execute(select(func.count()).select_from(WorkflowRun))).scalar_one()
            running_wf = (await session.execute(
                select(func.count()).select_from(WorkflowRun).where(WorkflowRun.status == "running")
            )).scalar_one()
            completed_wf = (await session.execute(
                select(func.count()).select_from(WorkflowRun).where(WorkflowRun.status == "completed")
            )).scalar_one()
            failed_wf = (await session.execute(
                select(func.count()).select_from(WorkflowRun).where(WorkflowRun.status == "failed")
            )).scalar_one()
            pending_approvals = (await session.execute(
                select(func.count()).select_from(WorkflowApproval).where(WorkflowApproval.status == "pending")
            )).scalar_one()
            total_artifacts = (await session.execute(select(func.count()).select_from(WorkflowArtifact))).scalar_one()
            total_decisions = (await session.execute(select(func.count()).select_from(Decision))).scalar_one()

            dashboard["factory_summary"] = {
                "workflows": {
                    "total": total_wf,
                    "running": running_wf,
                    "completed": completed_wf,
                    "failed": failed_wf,
                    "success_rate_pct": round((completed_wf / total_wf * 100) if total_wf else 0, 1),
                },
                "pending_approvals": pending_approvals,
                "total_artifacts": total_artifacts,
                "total_decisions": total_decisions,
            }

            # Per-product summary
            product_rows = await session.execute(
                select(
                    WorkflowRun.product_id,
                    func.count(WorkflowRun.id).label("total"),
                    func.sum(
                        __import__("sqlalchemy").case((WorkflowRun.status == "completed", 1), else_=0)
                    ).label("done"),
                    func.sum(
                        __import__("sqlalchemy").case((WorkflowRun.status == "running", 1), else_=0)
                    ).label("running"),
                    func.sum(
                        __import__("sqlalchemy").case((WorkflowRun.status == "failed", 1), else_=0)
                    ).label("failed"),
                ).group_by(WorkflowRun.product_id)
            )
            for row in product_rows:
                if row.product_id:
                    total = row.total or 0
                    done = row.done or 0
                    dashboard["products"].append({
                        "product_id": row.product_id,
                        "workflows": {"total": total, "done": done, "running": row.running or 0, "failed": row.failed or 0},
                        "completion_pct": round((done / total * 100) if total else 0, 1),
                    })

            # Recent 10 workflows (no internal IDs that expose auth info)
            recent = await session.execute(
                select(WorkflowRun.workflow_type, WorkflowRun.status, WorkflowRun.current_stage,
                       WorkflowRun.product_id, WorkflowRun.created_at)
                .order_by(WorkflowRun.created_at.desc())
                .limit(10)
            )
            dashboard["recent_activity"] = [
                {
                    "type": r.workflow_type,
                    "status": r.status,
                    "stage": r.current_stage,
                    "product": r.product_id,
                    "started": r.created_at.isoformat() if r.created_at else None,
                }
                for r in recent
            ]

    except Exception as exc:
        logger.warning("Dashboard DB query failed: %s", exc)
        dashboard["db_error"] = "Database unavailable"

    return dashboard


@router.post("/publish-iso")
async def publish_iso():
    """Create ISO Audit Hub + 12 sub-pages in Confluence (PRJ0-48)."""
    from app.services.iso_publisher import publish_iso_hub
    space = os.getenv("CONFLUENCE_SPACE_KEY", "PR")
    parent = os.getenv("CONFLUENCE_PARENT_PAGE_TITLE", "")
    result = await publish_iso_hub(space_key=space, parent_title=parent)
    return result


@router.get("/jira-hierarchy")
async def get_jira_hierarchy():
    """Fetch JIRA Feature/Epic/Story hierarchy (PRJ0-55)."""
    from app.services.jira_hierarchy_publisher import fetch_hierarchy
    project = os.getenv("JIRA_PROJECT_KEY", "PRJ0")
    features = await fetch_hierarchy(project)
    return [
        {
            "name": f.name,
            "done": f.done_count,
            "total": f.total_count,
            "epics": [
                {
                    "key": e.key,
                    "summary": e.summary,
                    "stories": [
                        {
                            "key": s.key,
                            "summary": s.summary,
                            "status": s.status,
                            "status_cat": s.status_cat,
                        }
                        for s in e.stories
                    ],
                }
                for e in f.epics
            ],
        }
        for f in features
    ]


@router.post("/publish-jira-hierarchy")
async def publish_jira_hierarchy():
    """Publish JIRA Feature/Epic/Story hierarchy to Confluence (PRJ0-55)."""
    from app.services.jira_hierarchy_publisher import publish_hierarchy_to_confluence
    result = await publish_hierarchy_to_confluence(
        project_key=os.getenv("JIRA_PROJECT_KEY", "PRJ0"),
        space_key=os.getenv("CONFLUENCE_SPACE_KEY", "PR"),
    )
    return result


@router.post("/publish/temporal-guide")
async def publish_temporal_guide():
    """Publish the Temporal knowledge page to Confluence (full-width, auto-generated)."""
    from app.services.temporal_page_publisher import publish_temporal_page
    result = await publish_temporal_page()
    if result.get("status") == "error":
        raise HTTPException(status_code=503, detail=result["detail"])
    return result


@router.post("/publish-uml-diagrams")
async def publish_uml_diagrams():
    """Publish all 7 UML architecture diagrams from guide/ HTML to Confluence (PRJ0-85)."""
    from app.services.uml_diagram_publisher import publish_uml_diagrams as _publish
    result = await _publish()
    if result.get("status") == "error":
        raise HTTPException(status_code=503, detail=result.get("reason", "publish failed"))
    return result
