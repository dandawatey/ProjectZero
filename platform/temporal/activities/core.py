"""Core Temporal activities for ProjectZeroFactory.

Every activity communicates with the FastAPI backend via httpx.
Requests include idempotent correlation_ids built from (feature_id, stage/action)
so retries are safe.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Any, Optional

import httpx
from temporalio import activity

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BACKEND_URL = os.getenv("PZ_BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT = float(os.getenv("PZ_REQUEST_TIMEOUT", "30"))

# Agent type mapping — determines which agent handles each stage
STAGE_AGENT_MAP: dict[str, str] = {
    "intake": "product_agent",
    "specification": "product_agent",
    "design": "design_agent",
    "architecture": "architecture_agent",
    "implementation": "coding_agent",
    "testing": "qa_agent",
    "review": "review_agent",
    "approval": "governance_agent",
    "release_readiness": "release_agent",
    "completion": "orchestrator_agent",
    # Bug-fix stages
    "triage": "triage_agent",
    "diagnosis": "debug_agent",
    "fix": "coding_agent",
    "deployment": "devops_agent",
    # QA stages
    "test_plan": "qa_agent",
    "unit_tests": "qa_agent",
    "integration_tests": "qa_agent",
    "e2e_tests": "qa_agent",
    "coverage_check": "qa_agent",
    "report": "qa_agent",
    # Deployment stages
    "build_check": "devops_agent",
    "security_scan": "security_agent",
    "staging_deploy": "devops_agent",
    "smoke_test": "qa_agent",
    "production_deploy": "devops_agent",
    "health_check": "devops_agent",
    # Release stages
    "changelog": "release_agent",
    "version_bump": "release_agent",
    "final_validation": "qa_agent",
    "stakeholder_approval": "governance_agent",
    "tag_release": "release_agent",
    "notify": "notification_agent",
}


# ---------------------------------------------------------------------------
# Data classes (mirrored from workflow definitions for deserialization)
# ---------------------------------------------------------------------------

@dataclass
class StepResult:
    step_name: str
    status: str  # completed | failed | blocked
    agent_id: Optional[str] = None
    artifacts: Optional[list] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _correlation_id(feature_id: str, action: str) -> str:
    """Deterministic idempotency key so Temporal retries are safe."""
    return f"{feature_id}:{action}:{uuid.uuid5(uuid.NAMESPACE_DNS, f'{feature_id}-{action}')}"


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=BACKEND_URL,
        timeout=REQUEST_TIMEOUT,
        headers={"Content-Type": "application/json"},
    )


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------

@activity.defn
async def sync_workflow_state(
    feature_id: str, status: str, stage: str
) -> dict:
    """POST workflow state to FastAPI backend for persistence."""
    correlation_id = _correlation_id(feature_id, f"sync_{status}_{stage}")
    async with _client() as client:
        response = await client.post(
            "/api/v1/workflows/state",
            json={
                "feature_id": feature_id,
                "status": status,
                "current_stage": stage,
                "correlation_id": correlation_id,
            },
        )
        response.raise_for_status()
        return response.json()


@activity.defn
async def record_step(
    feature_id: str, stage: str, status: str
) -> dict:
    """POST step progress to FastAPI backend."""
    correlation_id = _correlation_id(feature_id, f"step_{stage}_{status}")
    async with _client() as client:
        response = await client.post(
            "/api/v1/workflows/steps",
            json={
                "feature_id": feature_id,
                "stage": stage,
                "status": status,
                "correlation_id": correlation_id,
            },
        )
        response.raise_for_status()
        return response.json()


@activity.defn
async def request_approval(
    feature_id: str, stage: str
) -> dict:
    """Create a pending approval record in the backend.

    The Temporal workflow will block on a signal until the approval is granted
    externally (e.g. via the UI hitting a /approve endpoint that sends a signal).
    """
    correlation_id = _correlation_id(feature_id, f"approval_{stage}")
    async with _client() as client:
        response = await client.post(
            "/api/v1/approvals",
            json={
                "feature_id": feature_id,
                "stage": stage,
                "status": "pending",
                "correlation_id": correlation_id,
            },
        )
        response.raise_for_status()
        return response.json()


@activity.defn
async def execute_stage(
    feature_id: str, stage: str, product_id: str
) -> StepResult:
    """Assign an agent to the stage, execute it, and return the result.

    The backend is responsible for the actual agent orchestration. This activity
    calls the backend and waits for it to return the outcome.
    """
    agent_type = STAGE_AGENT_MAP.get(stage, "general_agent")
    correlation_id = _correlation_id(feature_id, f"exec_{stage}")

    async with _client() as client:
        # 1. Assign agent
        assign_resp = await client.post(
            "/api/v1/agents/assign",
            json={
                "feature_id": feature_id,
                "stage": stage,
                "product_id": product_id,
                "agent_type": agent_type,
                "correlation_id": correlation_id,
            },
        )
        assign_resp.raise_for_status()
        assignment = assign_resp.json()
        agent_id = assignment.get("agent_id", agent_type)

        # 2. Execute
        exec_resp = await client.post(
            "/api/v1/agents/execute",
            json={
                "feature_id": feature_id,
                "stage": stage,
                "product_id": product_id,
                "agent_id": agent_id,
                "correlation_id": correlation_id,
            },
        )
        exec_resp.raise_for_status()
        result_data = exec_resp.json()

        return StepResult(
            step_name=stage,
            status=result_data.get("status", "completed"),
            agent_id=agent_id,
            artifacts=result_data.get("artifacts"),
            error=result_data.get("error"),
        )


@activity.defn
async def assign_agent(
    feature_id: str, stage: str
) -> dict:
    """Determine and assign the correct agent type for a stage."""
    agent_type = STAGE_AGENT_MAP.get(stage, "general_agent")
    correlation_id = _correlation_id(feature_id, f"assign_{stage}")

    async with _client() as client:
        response = await client.post(
            "/api/v1/agents/assign",
            json={
                "feature_id": feature_id,
                "stage": stage,
                "agent_type": agent_type,
                "correlation_id": correlation_id,
            },
        )
        response.raise_for_status()
        return response.json()


@activity.defn
async def generate_artifact(
    feature_id: str, stage: str, artifact_type: str
) -> str:
    """Create an artifact record in the backend and return its ID."""
    correlation_id = _correlation_id(feature_id, f"artifact_{stage}_{artifact_type}")

    async with _client() as client:
        response = await client.post(
            "/api/v1/artifacts",
            json={
                "feature_id": feature_id,
                "stage": stage,
                "artifact_type": artifact_type,
                "correlation_id": correlation_id,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("artifact_id", "")


@activity.defn
async def create_audit_log(
    feature_id: str, action: str, details: dict[str, Any]
) -> dict:
    """POST an audit log entry to the backend."""
    correlation_id = _correlation_id(feature_id, f"audit_{action}")

    async with _client() as client:
        response = await client.post(
            "/api/v1/audit-logs",
            json={
                "feature_id": feature_id,
                "action": action,
                "details": details,
                "correlation_id": correlation_id,
            },
        )
        response.raise_for_status()
        return response.json()


@activity.defn
async def validate_input(input_data: dict) -> dict:
    """Validate workflow input against backend schema rules.

    Returns {"valid": True} or {"valid": False, "errors": [...]}.
    """
    async with _client() as client:
        response = await client.post(
            "/api/v1/workflows/validate",
            json=input_data,
        )
        response.raise_for_status()
        return response.json()


@activity.defn
async def finalize_workflow(feature_id: str) -> dict:
    """Mark a workflow as complete and trigger post-completion notifications."""
    correlation_id = _correlation_id(feature_id, "finalize")

    async with _client() as client:
        response = await client.post(
            "/api/v1/workflows/finalize",
            json={
                "feature_id": feature_id,
                "correlation_id": correlation_id,
            },
        )
        response.raise_for_status()
        return response.json()
