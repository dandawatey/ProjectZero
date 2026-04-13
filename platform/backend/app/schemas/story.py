from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class AcceptanceCriteriaCreate(BaseModel):
    given: str
    when_: str
    then_: str
    order: int = 0


class AcceptanceCriteriaRead(BaseModel):
    id: uuid.UUID
    story_id: uuid.UUID
    given: str
    when_: str
    then_: str
    order: int

    model_config = {"from_attributes": True}


class StoryCreate(BaseModel):
    workflow_run_id: uuid.UUID
    feature_id: str
    title: str
    role: str
    action: str
    benefit: str
    priority: int = 0
    criteria: list[AcceptanceCriteriaCreate] = []


class StoryRead(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    feature_id: str
    title: str
    role: str
    action: str
    benefit: str
    priority: int
    status: str
    created_at: datetime
    criteria: list[AcceptanceCriteriaRead] = []

    model_config = {"from_attributes": True}


class StoryUpdate(BaseModel):
    status: str  # draft / approved / rejected
