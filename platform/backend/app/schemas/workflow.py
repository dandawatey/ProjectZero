from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# WorkflowRun
# ---------------------------------------------------------------------------

class WorkflowRunCreate(BaseModel):
    workflow_type: str
    feature_id: str
    product_id: str | None = None
    config: dict[str, Any] | None = None


class WorkflowRunUpdate(BaseModel):
    status: str | None = None
    current_stage: str | None = None
    temporal_run_id: str | None = None


class WorkflowRunRead(BaseModel):
    id: uuid.UUID
    workflow_type: str
    feature_id: str
    product_id: str | None
    status: str
    current_stage: str | None
    temporal_run_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowRunList(BaseModel):
    items: list[WorkflowRunRead]
    total: int


# ---------------------------------------------------------------------------
# WorkflowStep
# ---------------------------------------------------------------------------

class WorkflowStepCreate(BaseModel):
    workflow_run_id: uuid.UUID
    stage_name: str
    status: str = "pending"
    agent_type: str | None = None
    agent_id: str | None = None
    correlation_id: str | None = None


class StepSyncRequest(BaseModel):
    """Idempotent step recording — keyed by correlation_id."""
    feature_id: str
    stage_name: str
    status: str
    agent_type: str | None = None
    agent_id: str | None = None
    correlation_id: str
    error_message: str | None = None


class WorkflowStepRead(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    stage_name: str
    status: str
    agent_type: str | None
    agent_id: str | None
    started_at: datetime | None
    completed_at: datetime | None
    correlation_id: str | None
    error_message: str | None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# WorkflowApproval
# ---------------------------------------------------------------------------

class WorkflowApprovalCreate(BaseModel):
    workflow_run_id: uuid.UUID
    stage_name: str
    approval_type: str  # checker / reviewer / approver


class ApprovalResolve(BaseModel):
    status: str  # approved / rejected
    resolved_by: str


class WorkflowApprovalRead(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    stage_name: str
    approval_type: str
    status: str
    requested_at: datetime
    resolved_at: datetime | None
    resolved_by: str | None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# WorkflowArtifact
# ---------------------------------------------------------------------------

class WorkflowArtifactCreate(BaseModel):
    workflow_run_id: uuid.UUID
    stage_name: str
    artifact_type: str
    content_path: str | None = None
    metadata: dict[str, Any] | None = None


class WorkflowArtifactRead(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    stage_name: str
    artifact_type: str
    content_path: str | None
    metadata: dict[str, Any] | None = Field(None, alias="metadata_")
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# ---------------------------------------------------------------------------
# WorkflowAudit
# ---------------------------------------------------------------------------

class WorkflowAuditCreate(BaseModel):
    workflow_run_id: uuid.UUID | None = None
    action: str
    agent_id: str | None = None
    details: dict[str, Any] | None = None
    correlation_id: str | None = None


class WorkflowAuditRead(BaseModel):
    id: int
    workflow_run_id: uuid.UUID | None
    action: str
    agent_id: str | None
    details: dict[str, Any] | None
    correlation_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# WorkflowTrigger
# ---------------------------------------------------------------------------

class WorkflowTriggerCreate(BaseModel):
    workflow_type: str
    trigger_type: str
    config: dict[str, Any] | None = None
    is_active: bool = True


class WorkflowTriggerUpdate(BaseModel):
    trigger_type: str | None = None
    config: dict[str, Any] | None = None
    is_active: bool | None = None


class WorkflowTriggerRead(BaseModel):
    id: uuid.UUID
    workflow_type: str
    trigger_type: str
    config: dict[str, Any] | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# AgentContribution
# ---------------------------------------------------------------------------

class AgentContributionCreate(BaseModel):
    workflow_run_id: uuid.UUID
    step_id: uuid.UUID | None = None
    agent_type: str
    agent_id: str
    action: str
    result: dict[str, Any] | None = None
    duration_ms: int | None = None


class AgentContributionRead(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    step_id: uuid.UUID | None
    agent_type: str
    agent_id: str
    action: str
    result: dict[str, Any] | None
    duration_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    active: int
    completed: int
    failed: int
    blocked: int
    pending_approvals: int
    recent_runs: list[WorkflowRunRead]
    recent_activity: list[WorkflowAuditRead]


# ---------------------------------------------------------------------------
# Signal
# ---------------------------------------------------------------------------

class WorkflowSignal(BaseModel):
    signal_name: str
    payload: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Catalog entry
# ---------------------------------------------------------------------------

class WorkflowCatalogEntry(BaseModel):
    workflow_type: str
    description: str
    stages: list[str]
