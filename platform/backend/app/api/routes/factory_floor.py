"""Factory Floor — single aggregated view of everything being built.

GET /api/v1/factory/floor
  → products[]         all products + sprint progress
  → in_flight[]        running workflow runs + live Temporal stage
  → pending_gates[]    approval gates waiting (with overdue flag)
  → recent_releases[]  last 10 completed releases from Brain
  → health{}           factory-wide counts

Temporal is queried for live current_stage per running workflow.
Falls back gracefully if Temporal is unreachable.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.workflow import WorkflowRun, WorkflowApproval, WorkflowArtifact
from app.models.brain import Memory

logger = logging.getLogger(__name__)
router = APIRouter()


async def _temporal_stage(workflow_run_id: str, temporal_run_id: str | None) -> str | None:
    """Query Temporal for live current_stage. Returns None if unavailable."""
    if not temporal_run_id:
        return None
    try:
        from app.temporal_integration.client import get_temporal_client
        client = await get_temporal_client()
        handle = client.get_workflow_handle(temporal_run_id)
        stage = await handle.query("current_stage")
        return stage
    except Exception:
        return None


@router.get("/floor")
async def factory_floor(db: AsyncSession = Depends(get_db)):
    """Single aggregated Factory Floor view."""

    now = datetime.now(timezone.utc)

    # ── 1. All workflow runs ──────────────────────────────────────────────────
    runs_q = await db.execute(
        select(WorkflowRun).order_by(WorkflowRun.updated_at.desc()).limit(200)
    )
    all_runs = runs_q.scalars().all()

    running_runs = [r for r in all_runs if r.status == "running"]
    completed_runs = [r for r in all_runs if r.status == "completed"]
    failed_runs = [r for r in all_runs if r.status == "failed"]

    # ── 2. Products — aggregate per product_id ────────────────────────────────
    product_map: dict[str, dict] = {}
    for run in all_runs:
        pid = run.product_id or "factory"
        if pid not in product_map:
            product_map[pid] = {
                "product_id": pid,
                "total": 0, "completed": 0, "running": 0, "failed": 0,
                "last_activity": None,
            }
        p = product_map[pid]
        p["total"] += 1
        if run.status == "completed":
            p["completed"] += 1
        elif run.status == "running":
            p["running"] += 1
        elif run.status == "failed":
            p["failed"] += 1
        if run.updated_at:
            ts = run.updated_at.replace(tzinfo=timezone.utc) if run.updated_at.tzinfo is None else run.updated_at
            if p["last_activity"] is None or ts > p["last_activity"]:
                p["last_activity"] = ts

    products = []
    for pid, p in product_map.items():
        total = p["total"] or 1
        products.append({
            "product_id": pid,
            "workflows": {
                "total": p["total"],
                "completed": p["completed"],
                "running": p["running"],
                "failed": p["failed"],
            },
            "completion_pct": round(p["completed"] / total * 100, 1),
            "last_activity": p["last_activity"].isoformat() if p["last_activity"] else None,
        })
    products.sort(key=lambda x: x["completion_pct"], reverse=True)

    # ── 3. In-flight — running workflows with live Temporal stage ─────────────
    in_flight = []
    for run in running_runs[:20]:
        live_stage = await _temporal_stage(str(run.id), run.temporal_run_id)
        started = run.created_at.replace(tzinfo=timezone.utc) if run.created_at and run.created_at.tzinfo is None else run.created_at
        elapsed_min = round((now - started).total_seconds() / 60, 1) if started else None
        in_flight.append({
            "workflow_run_id": str(run.id),
            "ticket_id": run.feature_id,
            "workflow_type": run.workflow_type,
            "product_id": run.product_id or "factory",
            "current_stage": live_stage or run.current_stage or "running",
            "started_at": started.isoformat() if started else None,
            "elapsed_min": elapsed_min,
            "temporal_id": run.temporal_run_id,
        })

    # ── 4. Pending approval gates ──────────────────────────────────────────────
    pending_q = await db.execute(
        select(WorkflowApproval)
        .where(WorkflowApproval.status == "pending")
        .order_by(WorkflowApproval.requested_at.asc())
    )
    pending_approvals = pending_q.scalars().all()

    gates = []
    for appr in pending_approvals:
        requested = appr.requested_at
        if requested and requested.tzinfo is None:
            requested = requested.replace(tzinfo=timezone.utc)
        waiting_h = round((now - requested).total_seconds() / 3600, 1) if requested else 0
        overdue = waiting_h > 24

        # Find parent workflow for context
        run_q = await db.execute(
            select(WorkflowRun).where(WorkflowRun.id == appr.workflow_run_id)
        )
        parent = run_q.scalar_one_or_none()

        gates.append({
            "approval_id": str(appr.id),
            "workflow_run_id": str(appr.workflow_run_id),
            "ticket_id": parent.feature_id if parent else "unknown",
            "product_id": parent.product_id if parent else "factory",
            "stage": appr.stage_name,
            "approval_type": appr.approval_type,
            "waiting_hours": waiting_h,
            "overdue": overdue,
            "requested_at": requested.isoformat() if requested else None,
        })

    # ── 5. Recent releases — from Brain memories tagged "release" ─────────────
    releases_q = await db.execute(
        select(Memory)
        .where(Memory.category == "release")
        .order_by(Memory.created_at.desc())
        .limit(10)
    )
    release_mems = releases_q.scalars().all()

    recent_releases = [
        {
            "key": m.key,
            "product_id": m.product_id or "factory",
            "content": m.content,
            "released_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in release_mems
    ]

    # ── 6. Factory health ──────────────────────────────────────────────────────
    total_artifacts_q = await db.execute(select(func.count(WorkflowArtifact.id)))
    total_artifacts = total_artifacts_q.scalar_one()

    health = {
        "workflows": {
            "total": len(all_runs),
            "running": len(running_runs),
            "completed": len(completed_runs),
            "failed": len(failed_runs),
            "success_rate_pct": round(len(completed_runs) / max(len(all_runs), 1) * 100, 1),
        },
        "pending_gates": len(gates),
        "overdue_gates": sum(1 for g in gates if g["overdue"]),
        "products_active": len([p for p in products if p["workflows"]["running"] > 0]),
        "total_artifacts": total_artifacts,
    }

    return {
        "generated_at": now.isoformat(),
        "health": health,
        "products": products,
        "in_flight": in_flight,
        "pending_gates": gates,
        "recent_releases": recent_releases,
    }
