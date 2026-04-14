"""Canonical execution models for Claude Execution Console — PRJ0-56."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class ExecStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"


class ExecutionEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str                          # workflow_start | step_start | step_end | agent_start | agent_end | ticket_done
    feature_id: Optional[str] = None        # e.g. "feature:agents"
    epic_key: Optional[str] = None          # e.g. "PRJ0-61"
    ticket_id: Optional[str] = None         # e.g. "PRJ0-49"
    workflow_run_id: Optional[str] = None
    workflow_name: Optional[str] = None
    step: Optional[str] = None              # e.g. "impl_activity"
    agent: Optional[str] = None             # e.g. "impl-agent"
    status: ExecStatus = ExecStatus.QUEUED
    pct: float = 0.0                        # 0-100
    elapsed_ms: Optional[int] = None
    retry_count: int = 0
    error: Optional[str] = None
    jira_url: Optional[str] = None
    temporal_url: Optional[str] = None
    log_url: Optional[str] = None
    trace_url: Optional[str] = None
    ts: datetime = Field(default_factory=datetime.utcnow)


class StatusSnapshot(BaseModel):
    features: list[FeatureStatus]
    overall_pct: float
    running_count: int
    failed_count: int
    queued_count: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class StepStatus(BaseModel):
    name: str
    status: ExecStatus
    agent: Optional[str] = None
    pct: float = 0.0
    elapsed_ms: Optional[int] = None
    retry_count: int = 0
    error: Optional[str] = None
    log_url: Optional[str] = None
    trace_url: Optional[str] = None


class WorkflowStatus(BaseModel):
    run_id: str
    workflow_name: str
    ticket_id: str
    status: ExecStatus
    pct: float = 0.0
    steps: list[StepStatus] = []
    temporal_url: Optional[str] = None


class TicketStatus(BaseModel):
    key: str
    summary: str
    status: ExecStatus
    pct: float = 0.0
    workflow: Optional[WorkflowStatus] = None
    jira_url: Optional[str] = None


class EpicStatus(BaseModel):
    key: str
    summary: str
    status: ExecStatus
    pct: float = 0.0
    tickets: list[TicketStatus] = []


class FeatureStatus(BaseModel):
    name: str
    status: ExecStatus
    pct: float = 0.0
    epics: list[EpicStatus] = []
