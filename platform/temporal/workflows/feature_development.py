"""Feature Development Workflow — the main multi-stage pipeline.

Stages: intake -> specification -> design -> architecture -> implementation
        -> testing -> review -> approval -> release_readiness -> completion

The 'review' stage spawns a MakerCheckerReviewerWorkflow child.
The 'approval' stage blocks on a human-sent Temporal signal.
Every stage transition is recorded to the FastAPI backend via the sync layer.
"""

from datetime import timedelta
from dataclasses import dataclass
from typing import Optional

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities.core import (
        sync_workflow_state,
        record_step,
        request_approval,
        execute_stage,
        create_audit_log,
        finalize_workflow,
    )

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FeatureInput:
    feature_id: str
    product_id: str
    title: str
    description: str
    priority: str
    created_by: str


@dataclass
class StepResult:
    step_name: str
    status: str  # completed | failed | blocked
    agent_id: Optional[str] = None
    artifacts: Optional[list] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STAGES = [
    "intake",
    "specification",
    "design",
    "architecture",
    "implementation",
    "testing",
    "review",
    "approval",
    "release_readiness",
    "completion",
]

DEFAULT_RETRY = RetryPolicy(
    maximum_attempts=3,
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
)


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

@workflow.defn
class FeatureDevelopmentWorkflow:
    """Orchestrates the full feature-development lifecycle."""

    def __init__(self) -> None:
        self._current_stage: str = ""
        self._approval_granted: bool = False
        self._blocked: bool = False
        self._block_reason: str = ""

    # -- Signals ------------------------------------------------------------

    @workflow.signal
    async def approve(self, approver_id: str) -> None:
        """Human sends this signal to unblock the approval gate."""
        self._approval_granted = True

    @workflow.signal
    async def unblock(self) -> None:
        """Resume a blocked workflow."""
        self._blocked = False
        self._block_reason = ""

    # -- Queries ------------------------------------------------------------

    @workflow.query
    def current_stage(self) -> str:
        return self._current_stage

    @workflow.query
    def is_blocked(self) -> bool:
        return self._blocked

    @workflow.query
    def block_reason(self) -> str:
        return self._block_reason

    # -- Run ----------------------------------------------------------------

    @workflow.run
    async def run(self, input: FeatureInput) -> dict:
        # Record workflow start
        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.feature_id, "started", "intake"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        await workflow.execute_activity(
            create_audit_log,
            args=[input.feature_id, "workflow_started", {
                "title": input.title,
                "created_by": input.created_by,
                "priority": input.priority,
            }],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        results: list[dict] = []

        for stage in STAGES:
            self._current_stage = stage

            # Record step start
            await workflow.execute_activity(
                record_step,
                args=[input.feature_id, stage, "in_progress"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=DEFAULT_RETRY,
            )

            # Execute the stage
            result = await self._execute_stage(input, stage)

            # Record step completion
            await workflow.execute_activity(
                record_step,
                args=[input.feature_id, stage, result.status],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=DEFAULT_RETRY,
            )

            results.append({
                "stage": stage,
                "status": result.status,
                "agent_id": result.agent_id,
                "error": result.error,
            })

            # Abort on failure
            if result.status == "failed":
                await workflow.execute_activity(
                    sync_workflow_state,
                    args=[input.feature_id, "failed", stage],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                await workflow.execute_activity(
                    create_audit_log,
                    args=[input.feature_id, "workflow_failed", {
                        "failed_at": stage,
                        "error": result.error,
                    }],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                return {"status": "failed", "failed_at": stage, "results": results}

        # Final sync & cleanup
        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.feature_id, "completed", "completion"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.execute_activity(
            finalize_workflow,
            args=[input.feature_id],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {"status": "completed", "results": results}

    # -- Helpers ------------------------------------------------------------

    async def _execute_stage(self, input: FeatureInput, stage: str) -> StepResult:
        """Dispatch a single stage to the correct handler."""

        if stage == "approval":
            return await self._handle_approval(input.feature_id, stage)
        elif stage == "review":
            return await self._handle_review(input.feature_id, stage)
        else:
            return await self._handle_activity(input.feature_id, stage, input.product_id)

    async def _handle_approval(self, feature_id: str, stage: str) -> StepResult:
        """Block until a human sends the `approve` signal."""
        self._approval_granted = False

        await workflow.execute_activity(
            request_approval,
            args=[feature_id, stage],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        # Block until signal arrives
        await workflow.wait_condition(lambda: self._approval_granted)

        await workflow.execute_activity(
            create_audit_log,
            args=[feature_id, "approval_granted", {"stage": stage}],
            start_to_close_timeout=timedelta(seconds=30),
        )
        return StepResult(step_name=stage, status="completed")

    async def _handle_review(self, feature_id: str, stage: str) -> StepResult:
        """Spawn MakerCheckerReviewerWorkflow as a child."""
        result: StepResult = await workflow.execute_child_workflow(
            MakerCheckerReviewerWorkflow.run,
            args=[feature_id, stage],
            id=f"mcr-{feature_id}-{stage}",
        )
        return result

    async def _handle_activity(
        self, feature_id: str, stage: str, product_id: str
    ) -> StepResult:
        """Assign an agent, execute the stage, return the result."""
        result: StepResult = await workflow.execute_activity(
            execute_stage,
            args=[feature_id, stage, product_id],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=DEFAULT_RETRY,
        )
        return result


# ---------------------------------------------------------------------------
# Child workflow: Maker-Checker-Reviewer
# ---------------------------------------------------------------------------

@workflow.defn
class MakerCheckerReviewerWorkflow:
    """Three-gate review: checker -> reviewer -> approver.

    Each gate creates a pending-approval record and blocks until the
    corresponding signal is received.
    """

    def __init__(self) -> None:
        self._checker_approved: bool = False
        self._reviewer_approved: bool = False
        self._approver_approved: bool = False

    # -- Signals ------------------------------------------------------------

    @workflow.signal
    async def checker_approve(self) -> None:
        self._checker_approved = True

    @workflow.signal
    async def reviewer_approve(self) -> None:
        self._reviewer_approved = True

    @workflow.signal
    async def approver_approve(self) -> None:
        self._approver_approved = True

    # -- Queries ------------------------------------------------------------

    @workflow.query
    def gate_status(self) -> dict:
        return {
            "checker": self._checker_approved,
            "reviewer": self._reviewer_approved,
            "approver": self._approver_approved,
        }

    # -- Run ----------------------------------------------------------------

    @workflow.run
    async def run(self, feature_id: str, stage: str) -> StepResult:
        retry = RetryPolicy(maximum_attempts=3)

        # Gate 1 — Checker
        await workflow.execute_activity(
            request_approval,
            args=[feature_id, f"{stage}_checker"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.wait_condition(lambda: self._checker_approved)

        await workflow.execute_activity(
            create_audit_log,
            args=[feature_id, "checker_approved", {"stage": stage}],
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Gate 2 — Reviewer
        await workflow.execute_activity(
            request_approval,
            args=[feature_id, f"{stage}_reviewer"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.wait_condition(lambda: self._reviewer_approved)

        await workflow.execute_activity(
            create_audit_log,
            args=[feature_id, "reviewer_approved", {"stage": stage}],
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Gate 3 — Approver
        await workflow.execute_activity(
            request_approval,
            args=[feature_id, f"{stage}_approver"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.wait_condition(lambda: self._approver_approved)

        await workflow.execute_activity(
            create_audit_log,
            args=[feature_id, "approver_approved", {"stage": stage}],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return StepResult(step_name=stage, status="completed")
