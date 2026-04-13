"""Release Governance Workflow — orchestrates the release lifecycle.

Stages: changelog -> version_bump -> final_validation -> stakeholder_approval
        -> tag_release -> notify
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
        generate_artifact,
        create_audit_log,
        finalize_workflow,
    )


@dataclass
class ReleaseInput:
    release_id: str
    product_id: str
    version: str
    release_type: str  # major | minor | patch | hotfix
    release_manager: str


@dataclass
class StepResult:
    step_name: str
    status: str
    agent_id: Optional[str] = None
    artifacts: Optional[list] = None
    error: Optional[str] = None


STAGES = [
    "changelog",
    "version_bump",
    "final_validation",
    "stakeholder_approval",
    "tag_release",
    "notify",
]

DEFAULT_RETRY = RetryPolicy(
    maximum_attempts=3,
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
)


@workflow.defn
class ReleaseGovernanceWorkflow:
    """Manages changelog generation, versioning, approval, tagging, and notification."""

    def __init__(self) -> None:
        self._current_stage: str = ""
        self._stakeholder_approved: bool = False

    @workflow.signal
    async def stakeholder_approve(self, approver_id: str) -> None:
        self._stakeholder_approved = True

    @workflow.query
    def current_stage(self) -> str:
        return self._current_stage

    @workflow.run
    async def run(self, input: ReleaseInput) -> dict:
        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.release_id, "started", "changelog"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        await workflow.execute_activity(
            create_audit_log,
            args=[input.release_id, "release_started", {
                "version": input.version,
                "release_type": input.release_type,
                "release_manager": input.release_manager,
            }],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        results: list[dict] = []
        release_artifacts: list[str] = []

        for stage in STAGES:
            self._current_stage = stage

            await workflow.execute_activity(
                record_step,
                args=[input.release_id, stage, "in_progress"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=DEFAULT_RETRY,
            )

            if stage == "stakeholder_approval":
                result = await self._handle_stakeholder_approval(
                    input.release_id, stage
                )
            elif stage == "changelog":
                result = await self._handle_changelog(input)
                artifact_id: str = await workflow.execute_activity(
                    generate_artifact,
                    args=[input.release_id, stage, "changelog"],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DEFAULT_RETRY,
                )
                release_artifacts.append(artifact_id)
            elif stage == "tag_release":
                result = await self._handle_tag_release(input)
                artifact_id = await workflow.execute_activity(
                    generate_artifact,
                    args=[input.release_id, stage, "release_tag"],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DEFAULT_RETRY,
                )
                release_artifacts.append(artifact_id)
            else:
                result: StepResult = await workflow.execute_activity(
                    execute_stage,
                    args=[input.release_id, stage, input.product_id],
                    start_to_close_timeout=timedelta(minutes=15),
                    retry_policy=DEFAULT_RETRY,
                )

            await workflow.execute_activity(
                record_step,
                args=[input.release_id, stage, result.status],
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
                    args=[input.release_id, "failed", stage],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                return {
                    "status": "failed",
                    "failed_at": stage,
                    "results": results,
                    "artifacts": release_artifacts,
                }

        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.release_id, "completed", "notify"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.execute_activity(
            finalize_workflow,
            args=[input.release_id],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {
            "status": "completed",
            "version": input.version,
            "results": results,
            "artifacts": release_artifacts,
        }

    # -- Stage handlers -----------------------------------------------------

    async def _handle_stakeholder_approval(
        self, release_id: str, stage: str
    ) -> StepResult:
        self._stakeholder_approved = False
        await workflow.execute_activity(
            request_approval,
            args=[release_id, stage],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )
        await workflow.wait_condition(lambda: self._stakeholder_approved)
        await workflow.execute_activity(
            create_audit_log,
            args=[release_id, "stakeholder_approved", {"stage": stage}],
            start_to_close_timeout=timedelta(seconds=30),
        )
        return StepResult(step_name=stage, status="completed")

    async def _handle_changelog(self, input: ReleaseInput) -> StepResult:
        result: StepResult = await workflow.execute_activity(
            execute_stage,
            args=[input.release_id, "changelog", input.product_id],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=DEFAULT_RETRY,
        )
        return result

    async def _handle_tag_release(self, input: ReleaseInput) -> StepResult:
        result: StepResult = await workflow.execute_activity(
            execute_stage,
            args=[input.release_id, "tag_release", input.product_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY,
        )
        await workflow.execute_activity(
            create_audit_log,
            args=[input.release_id, "release_tagged", {
                "version": input.version,
                "release_type": input.release_type,
            }],
            start_to_close_timeout=timedelta(seconds=30),
        )
        return result
