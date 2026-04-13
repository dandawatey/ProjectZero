"""Central activity tracking service — logs every user action."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import UserActivity, UserSession, SystemEvent


async def log_activity(
    db: AsyncSession,
    *,
    user_id: str,
    action: str,
    category: str,
    user_email: Optional[str] = None,
    user_role: Optional[str] = None,
    product_id: Optional[str] = None,
    workflow_run_id: Optional[UUID] = None,
    page: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    duration_ms: Optional[int] = None,
) -> UserActivity:
    """Log a user activity. Called from routes, middleware, or Temporal activities."""
    activity = UserActivity(
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        action=action,
        category=category,
        product_id=product_id,
        workflow_run_id=workflow_run_id,
        page=page,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        error_message=error_message,
        duration_ms=duration_ms,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def log_system_event(
    db: AsyncSession,
    *,
    event_type: str,
    source: str,
    message: str,
    severity: str = "info",
    details: Optional[dict] = None,
) -> SystemEvent:
    """Log a system event."""
    event = SystemEvent(
        event_type=event_type,
        source=source,
        severity=severity,
        message=message,
        details=details,
    )
    db.add(event)
    await db.commit()
    return event


async def get_activities(
    db: AsyncSession,
    *,
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    product_id: Optional[str] = None,
    action: Optional[str] = None,
    since: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[UserActivity]:
    """Query activities with filters."""
    query = select(UserActivity).order_by(desc(UserActivity.created_at))
    if user_id:
        query = query.where(UserActivity.user_id == user_id)
    if category:
        query = query.where(UserActivity.category == category)
    if product_id:
        query = query.where(UserActivity.product_id == product_id)
    if action:
        query = query.where(UserActivity.action == action)
    if since:
        query = query.where(UserActivity.created_at >= since)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_activity_summary(
    db: AsyncSession,
    *,
    hours: int = 24,
) -> dict:
    """Activity summary for dashboard."""
    since = datetime.utcnow() - timedelta(hours=hours)

    # Total activities
    total = await db.scalar(
        select(func.count(UserActivity.id)).where(UserActivity.created_at >= since)
    )

    # By category
    cat_query = (
        select(UserActivity.category, func.count(UserActivity.id))
        .where(UserActivity.created_at >= since)
        .group_by(UserActivity.category)
    )
    cat_result = await db.execute(cat_query)
    by_category = {row[0]: row[1] for row in cat_result}

    # By status
    status_query = (
        select(UserActivity.status, func.count(UserActivity.id))
        .where(UserActivity.created_at >= since)
        .group_by(UserActivity.status)
    )
    status_result = await db.execute(status_query)
    by_status = {row[0]: row[1] for row in status_result}

    # Active users
    active_users = await db.scalar(
        select(func.count(func.distinct(UserActivity.user_id)))
        .where(UserActivity.created_at >= since)
    )

    # Top actions
    action_query = (
        select(UserActivity.action, func.count(UserActivity.id).label("count"))
        .where(UserActivity.created_at >= since)
        .group_by(UserActivity.action)
        .order_by(desc("count"))
        .limit(10)
    )
    action_result = await db.execute(action_query)
    top_actions = [{"action": row[0], "count": row[1]} for row in action_result]

    # Recent system events
    events_query = (
        select(SystemEvent)
        .where(SystemEvent.created_at >= since)
        .order_by(desc(SystemEvent.created_at))
        .limit(20)
    )
    events_result = await db.execute(events_query)
    recent_events = events_result.scalars().all()

    return {
        "period_hours": hours,
        "total_activities": total or 0,
        "active_users": active_users or 0,
        "by_category": by_category,
        "by_status": by_status,
        "top_actions": top_actions,
        "recent_system_events": [
            {
                "type": e.event_type,
                "source": e.source,
                "severity": e.severity,
                "message": e.message,
                "created_at": e.created_at.isoformat(),
            }
            for e in recent_events
        ],
    }


async def get_user_timeline(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
) -> list[dict]:
    """Get chronological timeline for a specific user."""
    query = (
        select(UserActivity)
        .where(UserActivity.user_id == user_id)
        .order_by(desc(UserActivity.created_at))
        .limit(limit)
    )
    result = await db.execute(query)
    activities = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "action": a.action,
            "category": a.category,
            "product_id": a.product_id,
            "status": a.status,
            "details": a.details,
            "duration_ms": a.duration_ms,
            "created_at": a.created_at.isoformat(),
        }
        for a in activities
    ]
