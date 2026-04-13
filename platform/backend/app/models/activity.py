"""Central user activity tracking — every action logged."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class UserActivity(Base):
    """Every user action across the entire system. Central audit."""
    __tablename__ = "user_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Who
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(100), nullable=True)
    
    # What
    action = Column(String(255), nullable=False, index=True)  # e.g., "workflow.start", "approval.approve", "command.run"
    category = Column(String(100), nullable=False, index=True)  # workflow, approval, command, navigation, integration, agent
    
    # Where
    product_id = Column(String(255), nullable=True, index=True)
    workflow_run_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    page = Column(String(255), nullable=True)  # UI page where action occurred
    
    # Details
    details = Column(JSON, nullable=True)  # action-specific payload
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Result
    status = Column(String(50), default="success")  # success, failed, denied
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Time
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("ix_activity_user_time", "user_id", "created_at"),
        Index("ix_activity_category_time", "category", "created_at"),
        Index("ix_activity_product_time", "product_id", "created_at"),
    )


class UserSession(Base):
    """Track user sessions for activity correlation."""
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
    metadata_ = Column("metadata", JSON, nullable=True)


class SystemEvent(Base):
    """System-level events — integration changes, deployments, errors."""
    __tablename__ = "system_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)  # integration.connected, deployment.started, error.critical
    source = Column(String(100), nullable=False)  # backend, temporal, frontend, integration
    severity = Column(String(20), default="info")  # info, warning, error, critical
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
