"""Bug Fix Workflow — streamlined pipeline for defect resolution.

Stages: triage -> diagnosis -> fix -> testing -> review -> approval -> deployment
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


@dataclass
class BugFixInput:
    bug_id: str
    product_id: str
    title: str
    description: str
    severity: str  # critical | high | medium | low
    reported_by: str


@dataclass
class StepResult:
    step_name: str
    status: str
    agent_id: Optional[str] = None
    artifacts: Optional[list] = None
    error: Optional[str] = None


STAGES = [
    "triage",
    "diagnosis",
    "fix",
    "testing",
    "review",
    "approval",
    "deployment",
]

DEFAULT_RETRY = RetryPolicy(
    maximum_attempts=3,
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
)


@workflow.defn
class BugFixWorkflow:
    """Orchestrates a bug-fix lifecycle from triage through deployment."""

    def __init__(self) -> None:
        self._current_stage: str = ""
        self._approval_granted: bool = False

    @workflow.signal
    async def approve(self, approver_id: str) -> None:
        self._approval_granted = True

    @workflow.query
    def current_stage(self) -> str:
        return self._current_stage

    @workflow.run
    async def run(self, input: BugFixInput) -> dict:
        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.bug_id, "started", "triage"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        await workflow.execute_activity(
            create_audit_log,
            args=[input.bug_id, "bugfix_started", {
                "title": input.title,
                "severity": input.severity,
                "reported_by": input.reported_by,
            }],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        results: list[dict] = []

        for stage in STAGES:
            self._current_stage = stage

            await workflow.execute_activity(
                record_step,
                args=[input.bug_id, stage, "in_progress"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=DEFAULT_RETRY,
            )

            if stage == "approval":
                result = await self._handle_approval(input.bug_id, stage)
            else:
                # For critical bugs, use shorter timeout for triage/diagnosis
                timeout = timedelta(minutes=10) if (
                    input.severity == "critical" and stage in ("triage", "diagnosis")
                ) else timedelta(minutes=30)

                result = StepResult(
                    **(await workflow.execute_activity(
                        execute_stage,
                        args=[input.bug_id, stage, input.product_id],
                        start_to_close_timeout=timeout,
                        retry_policy=DEFAULT_RETRY,
                    )).__dict__
                )

            await workflow.execute_activity(
                record_step,
                args=[input.bug_id, stage, result.status],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=DEFAULT_RETRY,
            )

            results.append({
                "stage": stage,
                "status": result.status,
                "error": result.error,
            })

            if result.status == "failed":
                await workflow.execute_activity(
                    sync_workflow_state,
                    args=[input.bug_id, "failed", stage],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                return {"status": "failed", "failed_at": stage, "results": results}

        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.bug_id, "completed", "deployment"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.execute_activity(
            finalize_workflow,
            args=[input.bug_id],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {"status": "completed", "results": results}

    async def _handle_approval(self, bug_id: str, stage: str) -> StepResult:
        self._approval_granted = False
        await workflow.execute_activity(
            request_approval,
            args=[bug_id, stage],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )
        await workflow.wait_condition(lambda: self._approval_granted)
        await workflow.execute_activity(
            create_audit_log,
            args=[bug_id, "bugfix_approval_granted", {"stage": stage}],
            start_to_close_timeout=timedelta(seconds=30),
        )
        return StepResult(step_name=stage, status="completed")
