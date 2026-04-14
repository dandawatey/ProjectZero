"""Agent model — PRJ0-49.

Catalog of AI agents known to ProjectZeroFactory.
Each agent has a stable agent_id, skill set, model config, and lifecycle status.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(128), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    skills = Column(JSONB, nullable=False, default=list)
    model = Column(String(128), nullable=False, default="claude-sonnet-4-6")
    status = Column(String(20), nullable=False, default="active")  # active | inactive
    prompt_template_key = Column(String(255), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
