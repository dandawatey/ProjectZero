"""CXO metrics router — PRJ0-21 / PRJ0-41.

Endpoints:
  GET  /api/v1/cxo/portfolio                  — all projects summary cards
  GET  /api/v1/cxo/projects/{key}             — full metrics for one project (cached)
  POST /api/v1/cxo/projects/{key}/refresh     — force-refresh cache for one project
  POST /api/v1/cxo/publish                    — publish portfolio to Confluence (PRJ0-41)
  POST /api/v1/cxo/publish/{key}              — publish per-project page to Confluence (PRJ0-41)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

import os

from app.core.database import get_db
from app.models.metrics import CxoMetricsCache
from app.schemas.cxo import Portfolio, ProjectMetrics, ProjectSummary
from app.services.jira_client import JiraClient
from app.services.confluence_client import ConfluenceClient

router = APIRouter()


def _client() -> JiraClient:
    try:
        return JiraClient()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

@router.get("/portfolio", response_model=Portfolio)
async def portfolio(db: AsyncSession = Depends(get_db)):
    """Return summary card for every JIRA project."""
    jira = _client()
    async with httpx.AsyncClient() as c:
        projects = await jira.list_projects()
        summaries = []
        for p in projects:
            try:
                s = await jira.project_summary(c, p["key"])
                summaries.append(ProjectSummary(**s))
            except Exception:
                pass
    return Portfolio(projects=summaries)


# ---------------------------------------------------------------------------
# Per-project metrics (with cache)
# ---------------------------------------------------------------------------

@router.get("/projects/{key}", response_model=ProjectMetrics)
async def project_metrics(key: str, db: AsyncSession = Depends(get_db)):
    """Return full agile metrics for a project. Serves from cache when available."""
    key = key.upper()

    # Try cache
    result = await db.execute(select(CxoMetricsCache).where(CxoMetricsCache.project_key == key))
    cached = result.scalar_one_or_none()
    if cached:
        return ProjectMetrics(
            summary=cached.summary,
            velocity=cached.velocity or [],
            burndown=cached.burndown or {"sprint": None, "total": 0, "series": []},
            assignees=cached.assignees or [],
            cycle_time=cached.cycle_time or [],
            issue_types=cached.issue_types or [],
            throughput=cached.throughput or [],
            cached=True,
        )

    return await _fetch_and_cache(key, db)


@router.post("/projects/{key}/refresh", response_model=ProjectMetrics)
async def refresh_project(key: str, db: AsyncSession = Depends(get_db)):
    """Force-refresh cache for one project from JIRA."""
    return await _fetch_and_cache(key.upper(), db)


# ---------------------------------------------------------------------------
# Confluence publish (PRJ0-41)
# ---------------------------------------------------------------------------

def _confluence_client() -> ConfluenceClient:
    try:
        return ConfluenceClient()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


def _confluence_parent() -> str:
    return os.getenv("CONFLUENCE_PARENT_PAGE_TITLE", "ProjectZero Products")


@router.post("/publish", summary="Publish CXO portfolio to Confluence")
async def publish_portfolio(db: AsyncSession = Depends(get_db)):
    """Fetch all project summaries and publish a CXO Portfolio page to Confluence."""
    jira = _client()
    cf = _confluence_client()
    async with httpx.AsyncClient() as c:
        projects = await jira.list_projects()
        summaries = []
        for p in projects:
            try:
                s = await jira.project_summary(c, p["key"])
                summaries.append(s)
            except Exception:
                pass
    page_id = await cf.publish_cxo_portfolio(summaries, _confluence_parent())
    if not page_id:
        raise HTTPException(status_code=502, detail="Confluence publish failed")
    cf_base = os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")
    return {"page_id": page_id, "url": f"{cf_base}/pages/{page_id}"}


@router.post("/publish/{key}", summary="Publish per-project CXO page to Confluence")
async def publish_project(key: str, db: AsyncSession = Depends(get_db)):
    """Fetch metrics for one project and publish a Confluence page under CXO Portfolio."""
    key = key.upper()
    metrics = await _fetch_and_cache(key, db)
    cf = _confluence_client()
    page_id = await cf.publish_cxo_project(
        project_key=key,
        metrics=metrics.model_dump(),
        parent_title=_confluence_parent(),
    )
    if not page_id:
        raise HTTPException(status_code=502, detail="Confluence publish failed")
    cf_base = os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")
    return {"page_id": page_id, "url": f"{cf_base}/pages/{page_id}"}


async def _fetch_and_cache(key: str, db: AsyncSession) -> ProjectMetrics:
    jira = _client()
    async with httpx.AsyncClient() as c:
        try:
            summary, velocity, burndown, assignees, cycle_time, issue_types, throughput = (
                await jira.project_summary(c, key),
                await jira.project_velocity(c, key),
                await jira.project_burndown(c, key),
                await jira.tickets_per_assignee(c, key),
                await jira.cycle_time(c, key),
                await jira.issue_type_breakdown(c, key),
                await jira.throughput(c, key),
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"JIRA fetch failed: {e}")

    # Upsert cache
    result = await db.execute(select(CxoMetricsCache).where(CxoMetricsCache.project_key == key))
    row = result.scalar_one_or_none()
    if row:
        row.summary = summary
        row.velocity = velocity
        row.burndown = burndown
        row.assignees = assignees
        row.cycle_time = cycle_time
        row.issue_types = issue_types
        row.throughput = throughput
    else:
        row = CxoMetricsCache(
            project_key=key,
            summary=summary,
            velocity=velocity,
            burndown=burndown,
            assignees=assignees,
            cycle_time=cycle_time,
            issue_types=issue_types,
            throughput=throughput,
        )
        db.add(row)
    await db.commit()

    return ProjectMetrics(
        summary=ProjectSummary(**summary),
        velocity=velocity,
        burndown=burndown,
        assignees=assignees,
        cycle_time=cycle_time,
        issue_types=issue_types,
        throughput=throughput,
        cached=False,
    )
