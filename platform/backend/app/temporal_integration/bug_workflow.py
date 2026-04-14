"""BugFixWorkflow — Diagnose → Fix → Verify.

Risk-based approval gates:
  critical / high  → 1 human approval after Fix stage
  medium           → 1 human approval after Fix stage
  low              → auto-approve (no gates)

Signal protocol:  approve_stage(ApprovalSignal) — same as StoryWorkflow
Query protocol:   current_stage() → str, last_artifact() → str
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.temporal_integration.workflows import ApprovalSignal
    from app.temporal_integration.activities import AgentInput, AgentOutput
    from app.temporal_integration.bug_activities import (
        diagnose_activity,
        bugfix_activity,
        verify_activity,
    )

logger = logging.getLogger(__name__)

_RETRY = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=10))
_ACTIVITY_TIMEOUT = timedelta(minutes=10)


@dataclass
class BugWorkflowInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    repo_path: str
    jira_project_key: str
    ticket_id: str
    title: str
    description: str
    risk_level: str          # low | medium | high | critical
    auto_approve: bool


@workflow.defn(name="BugFixWorkflow")
class BugFixWorkflow:
    """Orchestrates Diagnose → Fix → Verify with risk-based approval."""

    def __init__(self) -> None:
        self._stage = "pending"
        self._last_artifact = ""
        self._approval: ApprovalSignal | None = None

    @workflow.signal
    async def approve_stage(self, sig: ApprovalSignal) -> None:
        self._approval = sig

    @workflow.query
    def current_stage(self) -> str:
        return self._stage

    @workflow.query
    def last_artifact(self) -> str:
        return self._last_artifact

    @workflow.run
    async def run(self, inp: BugWorkflowInput) -> dict:
        results: dict[str, AgentOutput] = {}

        # --- Stage 1: Diagnose ---
        self._stage = "diagnose"
        diag_out = await workflow.execute_activity(
            diagnose_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.ticket_id,
                stage="diagnose",
                context={
                    "title": inp.title,
                    "description": inp.description,
                    "risk_level": inp.risk_level,
                },
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = diag_out.artifact_path
        results["diagnose"] = diag_out

        if diag_out.status == "failed":
            return _to_dict(results, "failed")

        # --- Stage 2: Fix ---
        self._stage = "fix"
        fix_out = await workflow.execute_activity(
            bugfix_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.ticket_id,
                stage="fix",
                context={"diagnosis_artifact_path": diag_out.artifact_path},
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = fix_out.artifact_path
        results["fix"] = fix_out

        if fix_out.status == "failed":
            return _to_dict(results, "failed")

        # Human approval gate — only for medium/high/critical
        if not inp.auto_approve and inp.risk_level in ("medium", "high", "critical"):
            await self._wait_approval("fix")

        # --- Stage 3: Verify ---
        self._stage = "verify"
        verify_out = await workflow.execute_activity(
            verify_activity,
            AgentInput(
                workflow_run_id=inp.workflow_run_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=inp.ticket_id,
                stage="verify",
                context={"fix_artifact_path": fix_out.artifact_path},
            ),
            start_to_close_timeout=_ACTIVITY_TIMEOUT,
            retry_policy=_RETRY,
        )
        self._last_artifact = verify_out.artifact_path
        results["verify"] = verify_out

        self._stage = "completed"
        return _to_dict(results, "completed")

    async def _wait_approval(self, stage: str) -> None:
        self._approval = None
        await workflow.wait_condition(
            lambda: self._approval is not None and self._approval.stage == stage,
            timeout=timedelta(days=3),
        )
        if self._approval and not self._approval.approved:
            raise workflow.CancelledError(
                f"Stage '{stage}' rejected: {self._approval.comment}"
            )
        self._approval = None


def _to_dict(results: dict, final_status: str) -> dict:
    return {
        "status": final_status,
        "workflow": "BugFixWorkflow",
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
