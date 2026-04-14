import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), nullable=False, index=True)
    skill_id = Column(String(50), nullable=False, index=True)
    ticket_id = Column(String(50), nullable=True, index=True)   # JIRA key e.g. PRJ0-42
    workflow_run_id = Column(String(255), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="running")  # running|ok|failed|retried
    quality_gate_passed = Column(Boolean, nullable=True)
    brain_written = Column(Boolean, nullable=False, default=False)
    error_message = Column(String(1000), nullable=True)
