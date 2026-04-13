"""QA Validation Workflow — automated quality assurance pipeline.

Stages: test_plan -> unit_tests -> integration_tests -> e2e_tests
        -> coverage_check -> report
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
        execute_stage,
        generate_artifact,
        create_audit_log,
        finalize_workflow,
    )


@dataclass
class QAInput:
    feature_id: str
    product_id: str
    title: str
    target_coverage: float  # e.g. 0.80
    requested_by: str


@dataclass
class StepResult:
    step_name: str
    status: str
    agent_id: Optional[str] = None
    artifacts: Optional[list] = None
    error: Optional[str] = None


STAGES = [
    "test_plan",
    "unit_tests",
    "integration_tests",
    "e2e_tests",
    "coverage_check",
    "report",
]

DEFAULT_RETRY = RetryPolicy(
    maximum_attempts=3,
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
)


@workflow.defn
class QAValidationWorkflow:
    """Runs the full QA validation suite and produces a coverage report."""

    def __init__(self) -> None:
        self._current_stage: str = ""
        self._coverage_met: bool = False

    @workflow.query
    def current_stage(self) -> str:
        return self._current_stage

    @workflow.query
    def coverage_met(self) -> bool:
        return self._coverage_met

    @workflow.run
    async def run(self, input: QAInput) -> dict:
        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.feature_id, "started", "test_plan"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        await workflow.execute_activity(
            create_audit_log,
            args=[input.feature_id, "qa_started", {
                "title": input.title,
                "target_coverage": input.target_coverage,
                "requested_by": input.requested_by,
            }],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        results: list[dict] = []
        test_artifacts: list[str] = []

        for stage in STAGES:
            self._current_stage = stage

            await workflow.execute_activity(
                record_step,
                args=[input.feature_id, stage, "in_progress"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=DEFAULT_RETRY,
            )

            # Tests can take a while, give them more time
            timeout = timedelta(minutes=60) if stage in (
                "unit_tests", "integration_tests", "e2e_tests"
            ) else timedelta(minutes=15)

            result: StepResult = await workflow.execute_activity(
                execute_stage,
                args=[input.feature_id, stage, input.product_id],
                start_to_close_timeout=timeout,
                retry_policy=DEFAULT_RETRY,
            )

            # Generate artifacts for test stages
            if stage in ("unit_tests", "integration_tests", "e2e_tests", "coverage_check"):
                artifact_id: str = await workflow.execute_activity(
                    generate_artifact,
                    args=[input.feature_id, stage, f"{stage}_results"],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DEFAULT_RETRY,
                )
                test_artifacts.append(artifact_id)

            # Generate the final QA report artifact
            if stage == "report":
                report_id: str = await workflow.execute_activity(
                    generate_artifact,
                    args=[input.feature_id, stage, "qa_report"],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DEFAULT_RETRY,
                )
                test_artifacts.append(report_id)

            await workflow.execute_activity(
                record_step,
                args=[input.feature_id, stage, result.status],
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
                    args=[input.feature_id, "failed", stage],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                return {
                    "status": "failed",
                    "failed_at": stage,
                    "results": results,
                    "artifacts": test_artifacts,
                }

        # Mark coverage check outcome
        self._coverage_met = True

        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.feature_id, "completed", "report"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.execute_activity(
            finalize_workflow,
            args=[input.feature_id],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {
            "status": "completed",
            "results": results,
            "artifacts": test_artifacts,
            "coverage_met": self._coverage_met,
        }
