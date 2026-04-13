"""Temporal workflow definitions — PRJ0-43.

FeatureDevelopmentWorkflow:
  Stages: specification → architecture → realization → completion
  Each stage: run activity → await approval signal → advance

Signal protocol:
  approve_stage(stage_name)   → advance to next stage
  reject_stage(stage_name)    → fail workflow with reason

Query protocol:
  current_stage()             → str
  last_artifact()             → str (path)

Agent resolver (PRJ0-39):
  app.core.agent_resolver.STAGE_AGENT_MAP is the single source of truth for
  stage → activity name + agent_type + task_queue.

  Usage from workflow code:
    from app.core.agent_resolver import resolve_activity_name, agent_type_for_contribution
    activity_name = resolve_activity_name("realization", sub_step=0)  # "impl_activity"
    agent_type    = agent_type_for_contribution("realization", sub_step=1)  # "review-agent"

  The workflow below directly references activity functions for type safety.
  The resolver is the authoritative metadata layer — use it for dynamic dispatch,
  API exposure (/api/v1/commands/agent-map), and AgentContribution records.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.temporal_integration.activities import (
        AgentInput,
        AgentOutput,
        spec_activity,
        arch_activity,
        impl_activity,
        review_activity,
        deploy_activity,
    )

logger = logging.getLogger(__name__)

_RETRY = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=10))
_ACTIVITY_TIMEOUT = timedelta(minutes=15)


@dataclass
class WorkflowInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    repo_path: str
    jira_project_key: str
    feature_id: str


@dataclass
class ApprovalSignal:
    stage: str
    approved: bool
    comment: str = ""


@workflow.defn(name="FeatureDevelopmentWorkflow")
class FeatureDevelopmentWorkflow:
    """Orchestrates Spec→Arch→Impl→Review→Deploy across approval gates."""

    def __init__(self) -> None:
        self._stage = "pending"
        self._last_artifact = ""
        self._approval: ApprovalSignal | None = None
        self._artifacts: dict[str, str] = {}   # stage → artifact_path

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
            spec_activity,
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

        # Await human approval for spec
        await self._wait_approval("specification")

        # --- Stage 2: Architecture ---
        self._stage = "architecture"
        arch_out = await workflow.execute_activity(
            arch_activity,
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
            impl_activity,
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

        # --- Stage 3b: Review ---
        review_out = await workflow.execute_activity(
            review_activity,
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
            deploy_activity,
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
