"""Deployment Readiness Workflow — pre-production validation pipeline.

Stages: build_check -> security_scan -> staging_deploy -> smoke_test
        -> approval -> production_deploy -> health_check
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
class DeploymentInput:
    deployment_id: str
    product_id: str
    version: str
    environment: str  # staging | production
    initiated_by: str


@dataclass
class StepResult:
    step_name: str
    status: str
    agent_id: Optional[str] = None
    artifacts: Optional[list] = None
    error: Optional[str] = None


STAGES = [
    "build_check",
    "security_scan",
    "staging_deploy",
    "smoke_test",
    "approval",
    "production_deploy",
    "health_check",
]

DEFAULT_RETRY = RetryPolicy(
    maximum_attempts=3,
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
)


@workflow.defn
class DeploymentReadinessWorkflow:
    """Validates build, security, staging, and promotes to production."""

    def __init__(self) -> None:
        self._current_stage: str = ""
        self._approval_granted: bool = False
        self._rollback_requested: bool = False

    @workflow.signal
    async def approve(self, approver_id: str) -> None:
        self._approval_granted = True

    @workflow.signal
    async def request_rollback(self) -> None:
        self._rollback_requested = True

    @workflow.query
    def current_stage(self) -> str:
        return self._current_stage

    @workflow.query
    def rollback_requested(self) -> bool:
        return self._rollback_requested

    @workflow.run
    async def run(self, input: DeploymentInput) -> dict:
        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.deployment_id, "started", "build_check"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        await workflow.execute_activity(
            create_audit_log,
            args=[input.deployment_id, "deployment_started", {
                "version": input.version,
                "environment": input.environment,
                "initiated_by": input.initiated_by,
            }],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        results: list[dict] = []
        deploy_artifacts: list[str] = []

        for stage in STAGES:
            self._current_stage = stage

            # Check for rollback between stages
            if self._rollback_requested:
                await workflow.execute_activity(
                    create_audit_log,
                    args=[input.deployment_id, "rollback_triggered", {
                        "at_stage": stage,
                    }],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                await workflow.execute_activity(
                    sync_workflow_state,
                    args=[input.deployment_id, "rolled_back", stage],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                return {
                    "status": "rolled_back",
                    "rolled_back_at": stage,
                    "results": results,
                }

            await workflow.execute_activity(
                record_step,
                args=[input.deployment_id, stage, "in_progress"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=DEFAULT_RETRY,
            )

            if stage == "approval":
                result = await self._handle_approval(input.deployment_id, stage)
            elif stage == "security_scan":
                result = await self._handle_security_scan(input)
                # Generate security report artifact
                artifact_id: str = await workflow.execute_activity(
                    generate_artifact,
                    args=[input.deployment_id, stage, "security_report"],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DEFAULT_RETRY,
                )
                deploy_artifacts.append(artifact_id)
            elif stage in ("staging_deploy", "production_deploy"):
                result = await self._handle_deploy(input, stage)
            else:
                result: StepResult = await workflow.execute_activity(
                    execute_stage,
                    args=[input.deployment_id, stage, input.product_id],
                    start_to_close_timeout=timedelta(minutes=15),
                    retry_policy=DEFAULT_RETRY,
                )

            await workflow.execute_activity(
                record_step,
                args=[input.deployment_id, stage, result.status],
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
                    args=[input.deployment_id, "failed", stage],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                return {
                    "status": "failed",
                    "failed_at": stage,
                    "results": results,
                    "artifacts": deploy_artifacts,
                }

        await workflow.execute_activity(
            sync_workflow_state,
            args=[input.deployment_id, "completed", "health_check"],
            start_to_close_timeout=timedelta(seconds=30),
        )
        await workflow.execute_activity(
            finalize_workflow,
            args=[input.deployment_id],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {
            "status": "completed",
            "results": results,
            "artifacts": deploy_artifacts,
        }

    # -- Stage handlers -----------------------------------------------------

    async def _handle_approval(self, deployment_id: str, stage: str) -> StepResult:
        self._approval_granted = False
        await workflow.execute_activity(
            request_approval,
            args=[deployment_id, stage],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )
        await workflow.wait_condition(lambda: self._approval_granted)
        await workflow.execute_activity(
            create_audit_log,
            args=[deployment_id, "deployment_approved", {"stage": stage}],
            start_to_close_timeout=timedelta(seconds=30),
        )
        return StepResult(step_name=stage, status="completed")

    async def _handle_security_scan(self, input: DeploymentInput) -> StepResult:
        """Security scans get extra time and a dedicated artifact."""
        result: StepResult = await workflow.execute_activity(
            execute_stage,
            args=[input.deployment_id, "security_scan", input.product_id],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=DEFAULT_RETRY,
        )
        return result

    async def _handle_deploy(
        self, input: DeploymentInput, stage: str
    ) -> StepResult:
        """Deploy stages get extra time for infra operations."""
        result: StepResult = await workflow.execute_activity(
            execute_stage,
            args=[input.deployment_id, stage, input.product_id],
            start_to_close_timeout=timedelta(minutes=20),
            retry_policy=DEFAULT_RETRY,
        )
        await workflow.execute_activity(
            create_audit_log,
            args=[input.deployment_id, f"{stage}_completed", {
                "version": input.version,
                "environment": input.environment,
            }],
            start_to_close_timeout=timedelta(seconds=30),
        )
        return result
