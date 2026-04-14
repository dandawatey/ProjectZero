"""Agent Pydantic schemas — PRJ0-49."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AgentRead(BaseModel):
    id: str
    agent_id: str
    name: str
    skills: list[str]
    model: str
    status: str
    prompt_template_key: Optional[str]
    last_used_at: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}


class AgentCreate(BaseModel):
    agent_id: str
    name: str
    skills: list[str] = []
    model: str = "claude-sonnet-4-6"
    status: str = "active"
    prompt_template_key: Optional[str] = None


class AgentUpdate(BaseModel):
    status: Optional[str] = None
    model: Optional[str] = None
    prompt_template_key: Optional[str] = None
