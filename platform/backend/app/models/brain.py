"""ProjectZero Brain — persistent memory across sessions, products, conversations."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, Boolean, Float, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.core.database import Base


class Memory(Base):
    """Persistent memory entry. Survives sessions, searchable, promotable."""
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Scope
    scope = Column(String(50), nullable=False, index=True)  # factory, product, session
    product_id = Column(String(255), nullable=True, index=True)

    # Content
    category = Column(String(100), nullable=False, index=True)  # architecture, domain, decision, pattern, risk, learning
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), default=[])

    # Source
    source_agent = Column(String(100), nullable=True)
    source_workflow = Column(String(255), nullable=True)
    source_stage = Column(String(100), nullable=True)
    correlation_id = Column(String(255), nullable=True)

    # Quality
    confidence = Column(Float, default=0.8)  # 0-1
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    is_promoted = Column(Boolean, default=False)
    promoted_from = Column(UUID(as_uuid=True), nullable=True)

    # Lifecycle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_memory_scope_category", "scope", "category"),
        Index("ix_memory_product_category", "product_id", "category"),
    )


class Decision(Base):
    """Architecture and product decisions with full context."""
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(255), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    context = Column(Text, nullable=False)  # why decision was needed
    options = Column(JSON, nullable=False)  # [{option, pros, cons}]
    chosen = Column(String(255), nullable=False)
    rationale = Column(Text, nullable=False)
    decided_by = Column(String(100), nullable=False)  # agent or user
    decided_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="active")  # active, superseded, reversed
    superseded_by = Column(UUID(as_uuid=True), nullable=True)
    tags = Column(ARRAY(String), default=[])


class Pattern(Base):
    """Reusable patterns — proven approaches across products."""
    __tablename__ = "patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope = Column(String(50), nullable=False, index=True)  # factory, product
    category = Column(String(100), nullable=False, index=True)  # debug, test, review, uiux, architecture
    title = Column(String(500), nullable=False)
    problem = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    example = Column(Text, nullable=True)
    anti_pattern = Column(Text, nullable=True)  # what NOT to do

    # Validation
    proven_in = Column(ARRAY(String), default=[])  # product IDs where proven
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)
    status = Column(String(50), default="candidate")  # candidate, validated, promoted, rejected

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    """Persistent conversation/brainstorm history per workflow step."""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(255), nullable=False, index=True)
    workflow_run_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    stage = Column(String(100), nullable=True)

    # Mode
    mode = Column(String(50), nullable=False)  # chat, brainstorm, plan, implement

    # Content
    messages = Column(JSON, nullable=False, default=[])  # [{role, content, timestamp}]
    summary = Column(Text, nullable=True)  # AI-generated summary
    decisions_made = Column(JSON, default=[])  # decisions extracted from conversation
    action_items = Column(JSON, default=[])  # action items extracted

    # Lifecycle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
