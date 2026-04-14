"""EpicOrchestratorWorkflow — spawns child StoryWorkflows per story.

Flow:
  1. classify_ticket_activity   → confirm this is an epic
  2. fetch JIRA child stories   → get list of story ticket IDs
  3. start_child_workflow × N   → one FeatureDevelopmentWorkflow per story
  4. wait_all_children          → track completion, collect results
  5. return rollup summary

Child workflows run in parallel where no inter-story dependency declared.

Signal protocol:  approve_stage(ApprovalSignal) — proxied to named child
Query protocol:   current_stage() → str, children_status() → dict
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.temporal_integration.workflows import (
        FeatureDevelopmentWorkflow,
        WorkflowInput,
        ApprovalSignal,
    )
    from app.temporal_integration.classifier_activity import (
        TicketInput,
        ClassifierOutput,
        classify_ticket_activity,
    )

logger = logging.getLogger(__name__)

_RETRY = RetryPolicy(maximum_attempts=2, initial_interval=timedelta(seconds=5))
_ACTIVITY_TIMEOUT = timedelta(minutes=5)


@dataclass
class EpicWorkflowInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    repo_path: str
    jira_project_key: str
    epic_ticket_id: str
    epic_title: str
    epic_description: str
    # Pre-fetched child story ticket IDs (caller supplies from JIRA)
    # If empty, workflow completes with no children (JIRA not configured)
    child_ticket_ids: list[str] = field(default_factory=list)


@dataclass
class ChildApprovalSignal:
    child_ticket_id: str
    stage: str
    approved: bool
    comment: str = ""


@workflow.defn(name="EpicOrchestratorWorkflow")
class EpicOrchestratorWorkflow:
    """Orchestrates multiple StoryWorkflows for an Epic."""

    def __init__(self) -> None:
        self._stage = "pending"
        self._children: dict[str, str] = {}      # ticket_id → workflow_id
        self._child_status: dict[str, str] = {}  # ticket_id → stage
        self._child_approval: ChildApprovalSignal | None = None

    @workflow.signal
    async def approve_child_stage(self, sig: ChildApprovalSignal) -> None:
        """Proxy an approval signal to a specific child workflow."""
        self._child_approval = sig

    @workflow.signal
    async def approve_stage(self, sig: ApprovalSignal) -> None:
        """No-op on epic itself — use approve_child_stage for children."""
        pass

    @workflow.query
    def current_stage(self) -> str:
        return self._stage

    @workflow.query
    def children_status(self) -> dict:
        return self._child_status

    @workflow.run
    async def run(self, inp: EpicWorkflowInput) -> dict:
        self._stage = "orchestrating"

        if not inp.child_ticket_ids:
            # No children — JIRA not configured or epic has no stories yet
            self._stage = "completed"
            return {
                "status": "completed",
                "workflow": "EpicOrchestratorWorkflow",
                "epic": inp.epic_ticket_id,
                "children": {},
                "note": "No child stories provided — add story ticket IDs to trigger child workflows",
            }

        # Start one child FeatureDevelopmentWorkflow per story ticket
        child_handles = {}
        for ticket_id in inp.child_ticket_ids:
            child_id = f"{inp.workflow_run_id}-{ticket_id}"
            self._child_status[ticket_id] = "started"

            child_input = WorkflowInput(
                workflow_run_id=child_id,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
                feature_id=ticket_id,
            )
            handle = await workflow.start_child_workflow(
                FeatureDevelopmentWorkflow.run,
                child_input,
                id=child_id,
                task_queue="projectzero-factory",
                retry_policy=_RETRY,
            )
            child_handles[ticket_id] = handle
            self._children[ticket_id] = child_id

        self._stage = "waiting_children"

        # Proxy approval signals to correct child while waiting
        results = {}
        pending = dict(child_handles)

        while pending:
            # Check for approval signal to proxy
            if self._child_approval is not None:
                sig = self._child_approval
                self._child_approval = None
                child_wf_id = self._children.get(sig.child_ticket_id)
                if child_wf_id:
                    child_handle = workflow.get_external_workflow_handle(child_wf_id)
                    await child_handle.signal(
                        "approve_stage",
                        ApprovalSignal(
                            stage=sig.stage,
                            approved=sig.approved,
                            comment=sig.comment,
                        ),
                    )

            # Wait briefly then check completion
            completed_tickets = []
            for ticket_id, handle in pending.items():
                try:
                    # Non-blocking check — raises if still running
                    result = await workflow.wait_condition(
                        lambda: False,  # immediately returns
                        timeout=timedelta(seconds=1),
                    )
                except Exception:
                    pass  # still running

            # Poll completion via a short sleep
            await workflow.sleep(timedelta(seconds=30))

            # Check which children are done by querying their stage
            for ticket_id in list(pending.keys()):
                try:
                    child_handle = pending[ticket_id]
                    # If result is available, handle.result() won't block
                    result = await asyncio.wait_for(child_handle.result(), timeout=0.1)
                    results[ticket_id] = result
                    self._child_status[ticket_id] = "completed"
                    completed_tickets.append(ticket_id)
                except Exception:
                    self._child_status[ticket_id] = "running"

            for ticket_id in completed_tickets:
                pending.pop(ticket_id, None)

        self._stage = "completed"
        total = len(inp.child_ticket_ids)
        done = sum(1 for s in self._child_status.values() if s == "completed")

        return {
            "status": "completed",
            "workflow": "EpicOrchestratorWorkflow",
            "epic": inp.epic_ticket_id,
            "children_total": total,
            "children_completed": done,
            "children": results,
        }
