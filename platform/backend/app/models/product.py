"""Product model — PRJ0-42.

Each Product represents an isolated product git repo managed by ProjectZeroFactory.
All user project data (PRD, ADRs, code, .claude/memory/) lives in repo_path,
never inside ProjectZeroFactory itself.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    repo_path = Column(String(1024), nullable=False)
    jira_project_key = Column(String(50), nullable=True)
    github_url = Column(String(1024), nullable=True)
    confluence_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
