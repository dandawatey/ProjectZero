import uuid

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Story(Base):
    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_id = Column(String(200), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    role = Column(String(200), nullable=False)
    action = Column(Text, nullable=False)
    benefit = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="draft", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    criteria = relationship(
        "AcceptanceCriteria",
        back_populates="story",
        cascade="all, delete-orphan",
        order_by="AcceptanceCriteria.order",
    )


class AcceptanceCriteria(Base):
    __tablename__ = "acceptance_criteria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(
        UUID(as_uuid=True),
        ForeignKey("stories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    given = Column(Text, nullable=False)
    when_ = Column("when_", Text, nullable=False)
    then_ = Column("then_", Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)

    story = relationship("Story", back_populates="criteria")
