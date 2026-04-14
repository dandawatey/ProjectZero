"""FactorySelfBuildWorkflow — dogfood pipeline for PRJ0 tickets.

Identical stage flow to FeatureDevelopmentWorkflow:
  Spec → Arch → Impl → Review → Deploy

Uses factory-specific activities that are aware of the factory codebase
(FastAPI + React + Postgres + Temporal + Anthropic) and enforce factory
governance rules (MCRA, TDD, 80% coverage, no-ticket-no-work).

Signal protocol:  approve_stage(ApprovalSignal) — reused from workflows.py
Query protocol:   current_stage() → str, last_artifact() → str
"""

from __future__ import annotations

import logging
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    # Reuse shared data types from the product workflow
    from app.temporal_integration.workflows import (
        WorkflowInput,
        ApprovalSignal,
    )
    from app.temporal_integration.activities import AgentInput, AgentOutput
    from app.temporal_integration.factory_activities import (
        factory_spec_activity,
        factory_arch_activity,
        factory_impl_activity,
        factory_review_activity,
        factory_deploy_activity,
    )

logger = logging.getLogger(__name__)

_RETRY = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=10))
_ACTIVITY_TIMEOUT = timedelta(minutes=15)


@workflow.defn(name="FactorySelfBuildWorkflow")
class FactorySelfBuildWorkflow:
    """Orchestrates factory Spec→Arch→Impl→Review→Deploy across approval gates.

    Identical approval/query contract to FeatureDevelopmentWorkflow so the
    same frontend, CLI commands (/approve, /check), and Temporal UI work
    without modification.
    """

    def __init__(self) -> None:
        self._stage = "pending"
        self._last_artifact = ""
        self._approval: ApprovalSignal | None = None
        self._artifacts: dict[str, str] = {}  # stage → artifact_path

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    @workflow.signal
    async def approve_stage(self, sig: ApprovalSignal) -> None:
        self._approval = sig

    # ------------------------------------------------------------------
    # Query handlers
    # ------------------------------------------------------------------

    @workflow.query
    def current_stage(self) -> str:
        return self._stage

    @workflow.query
    def last_artifact(self) -> str:
        return self._last_artifact

    # ------------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------------

    @workflow.run
    async def run(self, inp: WorkflowInput) -> dict:
        results: dict[str, AgentOutput] = {}

        # --- Stage 1: Specification ---
        self._stage = "specification"
        spec_out = await workflow.execute_activity(
            factory_spec_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.feature_id,
                stage="specification",
                context={},
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = spec_out.artifact_path
        self._artifacts["specification"] = spec_out.artifact_path
        results["specification"] = spec_out

        if spec_out.status == "failed":
            return _to_dict(results, "failed")

        await self._wait_approval("specification")

        # --- Stage 2: Architecture ---
        self._stage = "architecture"
        arch_out = await workflow.execute_activity(
            factory_arch_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.feature_id,
                stage="architecture",
                context={"spec_artifact_path": spec_out.artifact_path},
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = arch_out.artifact_path
        self._artifacts["architecture"] = arch_out.artifact_path
        results["architecture"] = arch_out

        if arch_out.status == "failed":
            return _to_dict(results, "failed")

        await self._wait_approval("architecture")

        # --- Stage 3a: Implementation ---
        self._stage = "realization"
        impl_out = await workflow.execute_activity(
            factory_impl_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.feature_id,
                stage="realization",
                context={
                    "spec_artifact_path": spec_out.artifact_path,
                    "arch_artifact_path": arch_out.artifact_path,
                },
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = impl_out.artifact_path
        self._artifacts["impl"] = impl_out.artifact_path
        results["impl"] = impl_out

        # --- Stage 3b: Governance Review ---
        review_out = await workflow.execute_activity(
            factory_review_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.feature_id,
                stage="realization",
                context={"impl_artifact_path": impl_out.artifact_path},
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = review_out.artifact_path
        self._artifacts["review"] = review_out.artifact_path
        results["review"] = review_out

        if review_out.status == "failed":
            return _to_dict(results, "failed")

        await self._wait_approval("realization")

        # --- Stage 4: Completion / Deploy ---
        self._stage = "completion"
        deploy_out = await workflow.execute_activity(
            factory_deploy_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.feature_id,
                stage="completion",
                context={"review_artifact_path": review_out.artifact_path},
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = deploy_out.artifact_path
        self._artifacts["deployment"] = deploy_out.artifact_path
        results["deployment"] = deploy_out

        self._stage = "completed"
        return _to_dict(results, "completed")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _wait_approval(self, stage: str) -> None:
        """Block until approve_stage signal received for this stage."""
        self._approval = None
        await workflow.wait_condition(
            lambda: self._approval is not None and self._approval.stage == stage,
            timeout=timedelta(days=7),  # 7-day approval window
        )
        if self._approval and not self._approval.approved:
            raise workflow.CancelledError(
                f"Stage '{stage}' rejected: {self._approval.comment}"
            )
        self._approval = None


def _to_dict(results: dict, final_status: str) -> dict:
    return {
        "status": final_status,
        "workflow": "FactorySelfBuildWorkflow",
        "stages": {
            k: {
                "agent_type": v.agent_type,
                "status": v.status,
                "artifact_path": v.artifact_path,
                "summary": v.summary,
                "error": v.error,
            }
            for k, v in results.items()
        },
    }
