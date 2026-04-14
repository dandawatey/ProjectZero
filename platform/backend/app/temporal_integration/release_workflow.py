"""ReleaseWorkflow — verify → changelog → publish → [GATE] → notify."""

from __future__ import annotations

import logging
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.temporal_integration.workflows import ApprovalSignal
    from app.temporal_integration.release_activities import (
        ReleaseInput,
        verify_release_activity,
        generate_changelog_activity,
        publish_release_activity,
        notify_release_activity,
    )

logger = logging.getLogger(__name__)
_RETRY = RetryPolicy(maximum_attempts=2, initial_interval=timedelta(seconds=5))
_TIMEOUT = timedelta(minutes=5)


@workflow.defn(name="ReleaseWorkflow")
class ReleaseWorkflow:
    def __init__(self) -> None:
        self._stage = "pending"
        self._approval: ApprovalSignal | None = None

    @workflow.signal
    async def approve_stage(self, sig: ApprovalSignal) -> None:
        self._approval = sig

    @workflow.query
    def current_stage(self) -> str:
        return self._stage

    @workflow.run
    async def run(self, inp: ReleaseInput) -> dict:
        self._stage = "verifying"
        verify = await workflow.execute_activity(
            verify_release_activity, inp, start_to_close_timeout=_TIMEOUT, retry_policy=_RETRY)

        self._stage = "generating_changelog"
        changelog = await workflow.execute_activity(
            generate_changelog_activity, inp, verify, start_to_close_timeout=_TIMEOUT, retry_policy=_RETRY)

        self._stage = "publishing"
        publish = await workflow.execute_activity(
            publish_release_activity, inp, changelog, start_to_close_timeout=_TIMEOUT, retry_policy=_RETRY)

        if not inp.auto_approve:
            self._stage = "awaiting_approval"
            self._approval = None
            await workflow.wait_condition(
                lambda: self._approval is not None and self._approval.stage == "release",
                timeout=timedelta(hours=24))
            if self._approval and not self._approval.approved:
                return {"status": "rejected", "reason": self._approval.comment}

        self._stage = "notifying"
        await workflow.execute_activity(
            notify_release_activity, inp, start_to_close_timeout=_TIMEOUT, retry_policy=_RETRY)

        self._stage = "completed"
        return {
            "status": "completed", "workflow": "ReleaseWorkflow",
            "version": inp.version,
            "stories_done": verify.get("done", 0),
            "confluence_page": publish.get("page_id"),
        }
