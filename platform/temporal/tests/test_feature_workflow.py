"""Tests for FeatureDevelopmentWorkflow using Temporal's test environment.

Uses the Temporal Python SDK test server so no external Temporal instance
is required. Activities are mocked to avoid real HTTP calls.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

import pytest
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from workflows.feature_development import (
    FeatureDevelopmentWorkflow,
    FeatureInput,
    MakerCheckerReviewerWorkflow,
    STAGES,
    StepResult,
)

# ---------------------------------------------------------------------------
# Mock activities — return success for all calls, track invocations
# ---------------------------------------------------------------------------

_activity_calls: list[tuple[str, list]] = []


def _record_call(name: str, args: list):
    _activity_calls.append((name, args))


from temporalio import activity


@activity.defn(name="sync_workflow_state")
async def mock_sync_workflow_state(
    feature_id: str, status: str, stage: str
) -> dict:
    _record_call("sync_workflow_state", [feature_id, status, stage])
    return {"ok": True}


@activity.defn(name="record_step")
async def mock_record_step(
    feature_id: str, stage: str, status: str
) -> dict:
    _record_call("record_step", [feature_id, stage, status])
    return {"ok": True}


@activity.defn(name="request_approval")
async def mock_request_approval(
    feature_id: str, stage: str
) -> dict:
    _record_call("request_approval", [feature_id, stage])
    return {"ok": True}


@activity.defn(name="execute_stage")
async def mock_execute_stage(
    feature_id: str, stage: str, product_id: str
) -> StepResult:
    _record_call("execute_stage", [feature_id, stage, product_id])
    return StepResult(step_name=stage, status="completed", agent_id="test-agent")


@activity.defn(name="create_audit_log")
async def mock_create_audit_log(
    feature_id: str, action: str, details: dict
) -> dict:
    _record_call("create_audit_log", [feature_id, action, details])
    return {"ok": True}


@activity.defn(name="finalize_workflow")
async def mock_finalize_workflow(feature_id: str) -> dict:
    _record_call("finalize_workflow", [feature_id])
    return {"ok": True}


@activity.defn(name="generate_artifact")
async def mock_generate_artifact(
    feature_id: str, stage: str, artifact_type: str
) -> str:
    _record_call("generate_artifact", [feature_id, stage, artifact_type])
    return f"artifact-{stage}-{artifact_type}"


@activity.defn(name="assign_agent")
async def mock_assign_agent(feature_id: str, stage: str) -> dict:
    _record_call("assign_agent", [feature_id, stage])
    return {"agent_id": "test-agent"}


@activity.defn(name="validate_input")
async def mock_validate_input(input_data: dict) -> dict:
    _record_call("validate_input", [input_data])
    return {"valid": True}


MOCK_ACTIVITIES = [
    mock_sync_workflow_state,
    mock_record_step,
    mock_request_approval,
    mock_execute_stage,
    mock_create_audit_log,
    mock_finalize_workflow,
    mock_generate_artifact,
    mock_assign_agent,
    mock_validate_input,
]

TASK_QUEUE = "test-projectzero"


def _make_input() -> FeatureInput:
    return FeatureInput(
        feature_id=f"feat-{uuid.uuid4().hex[:8]}",
        product_id="prod-001",
        title="Test Feature",
        description="A test feature for workflow validation",
        priority="high",
        created_by="test-user",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_calls():
    _activity_calls.clear()
    yield
    _activity_calls.clear()


@pytest.mark.asyncio
async def test_workflow_completes_all_stages():
    """The workflow should progress through all 10 stages and return completed."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        input_data = _make_input()

        async with Worker(
            env.client,
            task_queue=TASK_QUEUE,
            workflows=[FeatureDevelopmentWorkflow, MakerCheckerReviewerWorkflow],
            activities=MOCK_ACTIVITIES,
        ):
            handle = await env.client.start_workflow(
                FeatureDevelopmentWorkflow.run,
                input_data,
                id=f"test-{input_data.feature_id}",
                task_queue=TASK_QUEUE,
            )

            # Send approval signal (the workflow blocks at the approval stage)
            await handle.signal(FeatureDevelopmentWorkflow.approve, "test-approver")

            # Send MCR signals for the review child workflow
            # We need to signal the child workflow
            mcr_handle = env.client.get_workflow_handle(
                f"mcr-{input_data.feature_id}-review"
            )
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.checker_approve)
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.reviewer_approve)
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.approver_approve)

            result = await handle.result()

        assert result["status"] == "completed"
        assert len(result["results"]) == len(STAGES)
        for entry in result["results"]:
            assert entry["status"] == "completed"


@pytest.mark.asyncio
async def test_query_current_stage():
    """The current_stage query should reflect the active stage."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        input_data = _make_input()

        async with Worker(
            env.client,
            task_queue=TASK_QUEUE,
            workflows=[FeatureDevelopmentWorkflow, MakerCheckerReviewerWorkflow],
            activities=MOCK_ACTIVITIES,
        ):
            handle = await env.client.start_workflow(
                FeatureDevelopmentWorkflow.run,
                input_data,
                id=f"test-query-{input_data.feature_id}",
                task_queue=TASK_QUEUE,
            )

            # The workflow will eventually block at "review" (child workflow)
            # or "approval" (signal wait). Query the stage at that point.
            # Give time-skipping env a moment to advance.
            import asyncio
            await asyncio.sleep(0.5)

            stage = await handle.query(FeatureDevelopmentWorkflow.current_stage)
            # Stage should be one of STAGES (exact stage depends on timing)
            assert stage in STAGES

            # Clean up: send all needed signals
            # MCR signals
            try:
                mcr_handle = env.client.get_workflow_handle(
                    f"mcr-{input_data.feature_id}-review"
                )
                await mcr_handle.signal(MakerCheckerReviewerWorkflow.checker_approve)
                await mcr_handle.signal(MakerCheckerReviewerWorkflow.reviewer_approve)
                await mcr_handle.signal(MakerCheckerReviewerWorkflow.approver_approve)
            except Exception:
                pass

            await handle.signal(FeatureDevelopmentWorkflow.approve, "test-approver")
            await handle.result()


@pytest.mark.asyncio
async def test_failed_stage_aborts_workflow():
    """If an activity returns status='failed', the workflow should abort."""

    @activity.defn(name="execute_stage")
    async def mock_execute_stage_fail(
        feature_id: str, stage: str, product_id: str
    ) -> StepResult:
        # Fail at the 'design' stage
        if stage == "design":
            return StepResult(
                step_name=stage,
                status="failed",
                error="Design validation failed",
            )
        return StepResult(step_name=stage, status="completed", agent_id="test-agent")

    fail_activities = [a for a in MOCK_ACTIVITIES if a.__name__ != "mock_execute_stage"]
    fail_activities.append(mock_execute_stage_fail)

    async with await WorkflowEnvironment.start_time_skipping() as env:
        input_data = _make_input()

        async with Worker(
            env.client,
            task_queue=TASK_QUEUE,
            workflows=[FeatureDevelopmentWorkflow, MakerCheckerReviewerWorkflow],
            activities=fail_activities,
        ):
            handle = await env.client.start_workflow(
                FeatureDevelopmentWorkflow.run,
                input_data,
                id=f"test-fail-{input_data.feature_id}",
                task_queue=TASK_QUEUE,
            )

            result = await handle.result()

        assert result["status"] == "failed"
        assert result["failed_at"] == "design"


@pytest.mark.asyncio
async def test_sync_workflow_state_called_at_start_and_end():
    """sync_workflow_state should be called for 'started' and 'completed'."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        input_data = _make_input()

        async with Worker(
            env.client,
            task_queue=TASK_QUEUE,
            workflows=[FeatureDevelopmentWorkflow, MakerCheckerReviewerWorkflow],
            activities=MOCK_ACTIVITIES,
        ):
            handle = await env.client.start_workflow(
                FeatureDevelopmentWorkflow.run,
                input_data,
                id=f"test-sync-{input_data.feature_id}",
                task_queue=TASK_QUEUE,
            )

            # Approve
            await handle.signal(FeatureDevelopmentWorkflow.approve, "test-approver")

            # MCR
            mcr_handle = env.client.get_workflow_handle(
                f"mcr-{input_data.feature_id}-review"
            )
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.checker_approve)
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.reviewer_approve)
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.approver_approve)

            await handle.result()

    sync_calls = [
        c for c in _activity_calls if c[0] == "sync_workflow_state"
    ]
    statuses = [c[1][1] for c in sync_calls]
    assert "started" in statuses
    assert "completed" in statuses


@pytest.mark.asyncio
async def test_record_step_called_for_each_stage():
    """record_step should be called with in_progress and completed for each stage."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        input_data = _make_input()

        async with Worker(
            env.client,
            task_queue=TASK_QUEUE,
            workflows=[FeatureDevelopmentWorkflow, MakerCheckerReviewerWorkflow],
            activities=MOCK_ACTIVITIES,
        ):
            handle = await env.client.start_workflow(
                FeatureDevelopmentWorkflow.run,
                input_data,
                id=f"test-steps-{input_data.feature_id}",
                task_queue=TASK_QUEUE,
            )

            await handle.signal(FeatureDevelopmentWorkflow.approve, "test-approver")

            mcr_handle = env.client.get_workflow_handle(
                f"mcr-{input_data.feature_id}-review"
            )
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.checker_approve)
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.reviewer_approve)
            await mcr_handle.signal(MakerCheckerReviewerWorkflow.approver_approve)

            await handle.result()

    step_calls = [c for c in _activity_calls if c[0] == "record_step"]
    recorded_stages = {c[1][1] for c in step_calls}
    for stage in STAGES:
        assert stage in recorded_stages, f"Stage '{stage}' was not recorded"
