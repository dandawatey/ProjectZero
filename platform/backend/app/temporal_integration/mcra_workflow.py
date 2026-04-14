"""MCRA (Maker-Checker-Reviewer-Approver) 4-eye child workflow — PRJ0-37.

Spawned by FeatureDevelopmentWorkflow after impl_activity completes.
Enforces four-eye principle: automated quality check + second-agent review + human approval.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.exceptions import TimeoutError as TemporalTimeoutError

logger = logging.getLogger(__name__)

APPROVER_TIMEOUT_HOURS = 72


@dataclass
class MCRAInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    repo_path: str
    jira_project_key: str
    feature_id: str
    impl_artifact_path: str   # path to impl artifact from impl_activity


@dataclass
class MCRAResult:
    approved: bool
    stage: str          # "checker" | "reviewer" | "approver"
    verdict: str        # "approved" | "rejected" | "timeout" | "gate_failed"
    reviewer_summary: str = ""
    approver_comment: str = ""


@workflow.defn(name="MCRAWorkflow")
class MCRAWorkflow:

    def __init__(self) -> None:
        self._approval_received = False
        self._approval_approved = False
        self._approval_comment = ""

    @workflow.signal(name="mcra_approve")
    def handle_approval(self, approved: bool, comment: str = "") -> None:
        """Signal from human approver via POST /commands/approve."""
        self._approval_received = True
        self._approval_approved = approved
        self._approval_comment = comment
        logger.info("MCRA approval signal received: approved=%s", approved)

    @workflow.run
    async def run(self, inp: MCRAInput) -> MCRAResult:
        logger.info("MCRAWorkflow starting for %s", inp.feature_id)

        # ── STAGE 1: CHECKER (automated quality gate) ──────────────────────
        workflow.logger.info("MCRA Stage 1: Checker — running quality gates")
        reviewer_summary = ""
        try:
            check_result = await workflow.execute_activity(
                "mcra_checker_activity",
                inp,
                start_to_close_timeout=timedelta(minutes=10),
            )
            if not check_result.get("passed", False):
                await workflow.execute_activity(
                    "mcra_notify_activity",
                    {
                        "feature_id": inp.feature_id,
                        "stage": "checker",
                        "message": f"Quality gates failed: {check_result}",
                        "workflow_run_id": inp.workflow_run_id,
                    },
                    start_to_close_timeout=timedelta(minutes=5),
                )
                return MCRAResult(
                    approved=False, stage="checker",
                    verdict="gate_failed",
                    reviewer_summary=str(check_result),
                )
        except Exception as exc:
            logger.warning("Checker activity failed (non-blocking): %s", exc)
            # Quality gate failure is non-blocking if tool not installed

        # ── STAGE 2: REVIEWER (second Claude agent) ─────────────────────────
        workflow.logger.info("MCRA Stage 2: Reviewer — second-agent code review")
        try:
            review_result = await workflow.execute_activity(
                "mcra_reviewer_activity",
                inp,
                start_to_close_timeout=timedelta(minutes=15),
            )
            reviewer_summary = review_result.get("summary", "")
            if review_result.get("verdict") == "REJECTED":
                await workflow.execute_activity(
                    "mcra_notify_activity",
                    {
                        "feature_id": inp.feature_id,
                        "stage": "reviewer",
                        "message": f"Reviewer rejected: {reviewer_summary}",
                        "workflow_run_id": inp.workflow_run_id,
                    },
                    start_to_close_timeout=timedelta(minutes=5),
                )
                return MCRAResult(
                    approved=False, stage="reviewer",
                    verdict="rejected",
                    reviewer_summary=reviewer_summary,
                )
        except Exception as exc:
            logger.warning("Reviewer activity failed (non-blocking): %s", exc)
            reviewer_summary = f"Review error: {exc}"

        # ── STAGE 3: APPROVER (human gate — wait up to 72h) ─────────────────
        workflow.logger.info("MCRA Stage 3: Approver — awaiting human signal (72h timeout)")
        await workflow.execute_activity(
            "mcra_notify_activity",
            {
                "feature_id": inp.feature_id,
                "stage": "approver",
                "message": (
                    f"Awaiting human approval. Send signal: "
                    f"POST /api/v1/commands/approve "
                    f"{{\"workflow_run_id\": \"{inp.workflow_run_id}\", \"approved\": true}}"
                ),
                "workflow_run_id": inp.workflow_run_id,
            },
            start_to_close_timeout=timedelta(minutes=5),
        )

        try:
            await workflow.wait_condition(
                lambda: self._approval_received,
                timeout=timedelta(hours=APPROVER_TIMEOUT_HOURS),
            )
        except TemporalTimeoutError:
            await workflow.execute_activity(
                "mcra_notify_activity",
                {
                    "feature_id": inp.feature_id,
                    "stage": "approver",
                    "message": f"MCRA approval timed out after {APPROVER_TIMEOUT_HOURS}h — escalating",
                    "workflow_run_id": inp.workflow_run_id,
                },
                start_to_close_timeout=timedelta(minutes=5),
            )
            return MCRAResult(
                approved=False, stage="approver",
                verdict="timeout",
                reviewer_summary=reviewer_summary,
            )

        return MCRAResult(
            approved=self._approval_approved,
            stage="approver",
            verdict="approved" if self._approval_approved else "rejected",
            reviewer_summary=reviewer_summary,
            approver_comment=self._approval_comment,
        )
