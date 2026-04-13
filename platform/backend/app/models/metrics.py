"""CXO metrics cache model — PRJ0-20.

Caches JIRA-derived agile metrics per project so the dashboard
doesn't hammer the JIRA API on every page load. Auto-created by
FastAPI lifespan via Base.metadata.create_all.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class CxoMetricsCache(Base):
    __tablename__ = "cxo_metrics_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_key = Column(String(50), nullable=False, unique=True, index=True)
    summary = Column(JSON, nullable=True)        # total / done / in_progress / todo / pct
    velocity = Column(JSON, nullable=True)       # list[{sprint, committed, completed, end_date}]
    burndown = Column(JSON, nullable=True)       # {sprint, total, series[{date, remaining}]}
    assignees = Column(JSON, nullable=True)      # list[{assignee, todo, in_progress}]
    cycle_time = Column(JSON, nullable=True)     # list[{key, days}]
    issue_types = Column(JSON, nullable=True)    # list[{type, count}]
    throughput = Column(JSON, nullable=True)     # list[{date, done}]
    cached_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
