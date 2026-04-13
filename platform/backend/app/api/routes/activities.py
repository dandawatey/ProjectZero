"""User activity monitoring routes."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.activity_service import (
    log_activity,
    get_activities,
    get_activity_summary,
    get_user_timeline,
    log_system_event,
)

router = APIRouter()


@router.post("/track")
async def track_activity(
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """Track a user activity. Called by frontend, CLI, or integrations."""
    activity = await log_activity(
        db,
        user_id=body.get("user_id", "anonymous"),
        action=body["action"],
        category=body["category"],
        user_email=body.get("user_email"),
        user_role=body.get("user_role"),
        product_id=body.get("product_id"),
        workflow_run_id=UUID(body["workflow_run_id"]) if body.get("workflow_run_id") else None,
        page=body.get("page"),
        details=body.get("details"),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        status=body.get("status", "success"),
        error_message=body.get("error_message"),
        duration_ms=body.get("duration_ms"),
    )
    return {"id": str(activity.id), "status": "tracked"}


@router.get("/")
async def list_activities(
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    product_id: Optional[str] = None,
    action: Optional[str] = None,
    hours: int = Query(default=24, le=720),
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List activities with filters."""
    since = datetime.utcnow() - timedelta(hours=hours)
    activities = await get_activities(
        db,
        user_id=user_id,
        category=category,
        product_id=product_id,
        action=action,
        since=since,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(a.id),
            "user_id": a.user_id,
            "action": a.action,
            "category": a.category,
            "product_id": a.product_id,
            "workflow_run_id": str(a.workflow_run_id) if a.workflow_run_id else None,
            "page": a.page,
            "status": a.status,
            "details": a.details,
            "duration_ms": a.duration_ms,
            "created_at": a.created_at.isoformat(),
        }
        for a in activities
    ]


@router.get("/summary")
async def activity_summary(
    hours: int = Query(default=24, le=720),
    db: AsyncSession = Depends(get_db),
):
    """Activity summary for monitoring dashboard."""
    return await get_activity_summary(db, hours=hours)


@router.get("/user/{user_id}/timeline")
async def user_timeline(
    user_id: str,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Chronological timeline for a specific user."""
    return await get_user_timeline(db, user_id, limit=limit)


@router.post("/system-event")
async def track_system_event(
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """Log a system event."""
    event = await log_system_event(
        db,
        event_type=body["event_type"],
        source=body["source"],
        message=body["message"],
        severity=body.get("severity", "info"),
        details=body.get("details"),
    )
    return {"id": str(event.id), "status": "logged"}
