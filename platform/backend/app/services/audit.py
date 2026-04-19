"""Audit logging service for immutable compliance logs."""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
import json
from typing import Optional, Any

from app.models.organization import AuditLog


async def log_audit_event(
    db: AsyncSession,
    org_id: uuid.UUID,
    actor_id: Optional[uuid.UUID],
    resource_type: str,
    resource_id: uuid.UUID,
    action: str,
    changes: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """
    Log an immutable audit event.

    Args:
        db: Database session
        org_id: Organization ID (tenant)
        actor_id: User ID performing action
        resource_type: Type of resource (organization, user, subscription, etc.)
        resource_id: ID of affected resource
        action: Action performed (created, updated, deleted, etc.)
        changes: JSON string of what changed
        ip_address: Client IP (for security context)
        user_agent: Client user agent

    Returns:
        Created AuditLog entry
    """
    log_entry = AuditLog(
        org_id=org_id,
        actor_id=actor_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.utcnow(),
    )

    db.add(log_entry)
    await db.flush()  # Insert but don't commit (caller controls transaction)

    return log_entry


async def get_audit_logs(
    db: AsyncSession,
    org_id: uuid.UUID,
    action: Optional[str] = None,
    actor_id: Optional[uuid.UUID] = None,
    resource_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditLog]:
    """
    Query audit logs with optional filters.

    Args:
        db: Database session
        org_id: Organization ID (required, tenant isolation)
        action: Filter by action
        actor_id: Filter by actor
        resource_type: Filter by resource type
        limit: Max results
        offset: Pagination offset

    Returns:
        List of AuditLog entries
    """
    from sqlalchemy.future import select

    stmt = select(AuditLog).where(AuditLog.org_id == org_id)

    if action:
        stmt = stmt.where(AuditLog.action == action)
    if actor_id:
        stmt = stmt.where(AuditLog.actor_id == actor_id)
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)

    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()
