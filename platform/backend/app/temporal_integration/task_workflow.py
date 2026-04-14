"""TaskWorkflow — Impl → Review (auto-approve, no gates).

For chores, docs, config changes, dependency bumps.
No human approval required — completes automatically.

Signal protocol:  approve_stage(ApprovalSignal) — kept for consistency
Query protocol:   current_stage() → str, last_artifact() → str
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.temporal_integration.workflows import ApprovalSignal
    from app.temporal_integration.activities import AgentInput, AgentOutput
    from app.temporal_integration.task_activities import (
        task_impl_activity,
        task_review_activity,
    )

logger = logging.getLogger(__name__)

_RETRY = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=5))
_ACTIVITY_TIMEOUT = timedelta(minutes=5)


@dataclass
class TaskWorkflowInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    repo_path: str
    jira_project_key: str
    ticket_id: str
    title: str
    description: str


@workflow.defn(name="TaskWorkflow")
class TaskWorkflow:
    """Orchestrates Impl → Review with no human gates."""

    def __init__(self) -> None:
        self._stage = "pending"
        self._last_artifact = ""

    @workflow.signal
    async def approve_stage(self, sig: ApprovalSignal) -> None:
        pass  # No-op — TaskWorkflow is fully automated

    @workflow.query
    def current_stage(self) -> str:
        return self._stage

    @workflow.query
    def last_artifact(self) -> str:
        return self._last_artifact

    @workflow.run
    async def run(self, inp: TaskWorkflowInput) -> dict:
        results: dict[str, AgentOutput] = {}

        # --- Stage 1: Implement ---
        self._stage = "implement"
        impl_out = await workflow.execute_activity(
            task_impl_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.ticket_id,
                stage="implement",
                context={"title": inp.title, "description": inp.description},
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = impl_out.artifact_path
        results["implement"] = impl_out

        if impl_out.status == "failed":
            return _to_dict(results, "failed")

        # --- Stage 2: Review (lightweight, no gate) ---
        self._stage = "review"
        review_out = await workflow.execute_activity(
            task_review_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.ticket_id,
                stage="review",
                context={"impl_artifact_path": impl_out.artifact_path},
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = review_out.artifact_path
        results["review"] = review_out

        self._stage = "completed"
        return _to_dict(results, "completed")


def _to_dict(results: dict, final_status: str) -> dict:
    return {
        "status": final_status,
        "workflow": "TaskWorkflow",
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
