import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_type = Column(String(100), nullable=False, index=True)
    feature_id = Column(String(200), nullable=False, index=True)
    product_id = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    current_stage = Column(String(100), nullable=True)
    temporal_run_id = Column(String(200), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    steps = relationship("WorkflowStep", back_populates="workflow_run", cascade="all, delete-orphan")
    approvals = relationship("WorkflowApproval", back_populates="workflow_run", cascade="all, delete-orphan")
    artifacts = relationship("WorkflowArtifact", back_populates="workflow_run", cascade="all, delete-orphan")
    audit_entries = relationship("WorkflowAudit", back_populates="workflow_run")
    agent_contributions = relationship("AgentContribution", back_populates="workflow_run", cascade="all, delete-orphan")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    agent_type = Column(String(100), nullable=True)
    agent_id = Column(String(200), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    correlation_id = Column(String(200), nullable=True, unique=True)
    error_message = Column(Text, nullable=True)

    workflow_run = relationship("WorkflowRun", back_populates="steps")
    agent_contributions = relationship("AgentContribution", back_populates="step", cascade="all, delete-orphan")


class WorkflowApproval(Base):
    __tablename__ = "workflow_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_name = Column(String(100), nullable=False)
    approval_type = Column(String(50), nullable=False)  # checker / reviewer / approver
    status = Column(String(50), nullable=False, default="pending")  # pending / approved / rejected
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String(200), nullable=True)

    workflow_run = relationship("WorkflowRun", back_populates="approvals")


class WorkflowArtifact(Base):
    __tablename__ = "workflow_artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_name = Column(String(100), nullable=False)
    artifact_type = Column(String(100), nullable=False)
    content_path = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    workflow_run = relationship("WorkflowRun", back_populates="artifacts")


class WorkflowAudit(Base):
    __tablename__ = "workflow_audit"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(200), nullable=False)
    agent_id = Column(String(200), nullable=True)
    details = Column(JSON, nullable=True)
    correlation_id = Column(String(200), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    workflow_run = relationship("WorkflowRun", back_populates="audit_entries")


class WorkflowTrigger(Base):
    __tablename__ = "workflow_triggers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_type = Column(String(100), nullable=False, index=True)
    trigger_type = Column(String(50), nullable=False)  # manual / api / webhook / schedule / agent / dependency
    config = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AgentContribution(Base):
    __tablename__ = "agent_contributions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_type = Column(String(100), nullable=False)
    agent_id = Column(String(200), nullable=False)
    action = Column(String(200), nullable=False)
    result = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    workflow_run = relationship("WorkflowRun", back_populates="agent_contributions")
    step = relationship("WorkflowStep", back_populates="agent_contributions")
