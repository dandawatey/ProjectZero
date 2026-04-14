"""TicketRouterWorkflow — entry point for ALL ticket types.

Flow:
  1. classify_ticket_activity   → determine workflow_type + risk_level
  2. route to correct workflow:
       epic  → EpicOrchestratorWorkflow  (child workflow)
       story → FeatureDevelopmentWorkflow (child workflow)
       bug   → BugFixWorkflow             (child workflow)
       task  → TaskWorkflow               (child workflow)

Query:  current_stage() → str, classification() → dict
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.temporal_integration.classifier_activity import (
        TicketInput,
        ClassifierOutput,
        classify_ticket_activity,
    )
    from app.temporal_integration.workflows import (
        FeatureDevelopmentWorkflow,
        WorkflowInput,
        ApprovalSignal,
    )
    from app.temporal_integration.bug_workflow import BugFixWorkflow, BugWorkflowInput
    from app.temporal_integration.task_workflow import TaskWorkflow, TaskWorkflowInput
    from app.temporal_integration.epic_workflow import EpicOrchestratorWorkflow, EpicWorkflowInput

logger = logging.getLogger(__name__)

_RETRY = RetryPolicy(maximum_attempts=2, initial_interval=timedelta(seconds=5))
_CLASSIFIER_TIMEOUT = timedelta(minutes=3)


@dataclass
class TicketRouterInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    repo_path: str
    jira_project_key: str
    ticket_id: str
    ticket_type: str          # Epic | Story | Bug | Task | Sub-task
    title: str
    description: str
    # For epics: pre-fetched child story IDs
    child_ticket_ids: list[str] = field(default_factory=list)


@workflow.defn(name="TicketRouterWorkflow")
class TicketRouterWorkflow:
    """Classifies a ticket then starts the correct child workflow."""

    def __init__(self) -> None:
        self._stage = "classifying"
        self._classification: dict = {}
        self._child_workflow_id: str = ""

    @workflow.signal
    async def approve_stage(self, sig: ApprovalSignal) -> None:
        """Proxy approval to child workflow."""
        if self._child_workflow_id:
            handle = workflow.get_external_workflow_handle(self._child_workflow_id)
            await handle.signal("approve_stage", sig)

    @workflow.query
    def current_stage(self) -> str:
        return self._stage

    @workflow.query
    def classification(self) -> dict:
        return self._classification

    @workflow.run
    async def run(self, inp: TicketRouterInput) -> dict:
        # --- Step 1: Classify ---
        self._stage = "classifying"
        clf: ClassifierOutput = await workflow.execute_activity(
            classify_ticket_activity,
            TicketInput(
                ticket_id=inp.ticket_id,
                title=inp.title,
                description=inp.description,
                ticket_type=inp.ticket_type,
                product_id=inp.product_id,
                product_name=inp.product_name,
                repo_path=inp.repo_path,
                jira_project_key=inp.jira_project_key,
            ),
            start_to_close_timeout=_CLASSIFIER_TIMEOUT,
            retry_policy=_RETRY,
        )

        self._classification = {
            "workflow_type": clf.workflow_type,
            "risk_level": clf.risk_level,
            "requires_spec": clf.requires_spec,
            "requires_arch": clf.requires_arch,
            "auto_approve": clf.auto_approve,
            "approval_count": clf.approval_count,
            "reason": clf.routing_reason,
        }

        child_id = f"{inp.workflow_run_id}-child"
        self._child_workflow_id = child_id
        self._stage = f"routed_to_{clf.workflow_type}"

        # --- Step 2: Route ---
        if clf.workflow_type == "epic":
            handle = await workflow.start_child_workflow(
                EpicOrchestratorWorkflow.run,
                EpicWorkflowInput(
                    workflow_run_id=child_id,
                    product_id=inp.product_id,
                    product_name=inp.product_name,
                    repo_path=inp.repo_path,
                    jira_project_key=inp.jira_project_key,
                    epic_ticket_id=inp.ticket_id,
                    epic_title=inp.title,
                    epic_description=inp.description,
                    child_ticket_ids=inp.child_ticket_ids,
                ),
                id=child_id,
                task_queue="projectzero-factory",
            )

        elif clf.workflow_type == "bug":
            handle = await workflow.start_child_workflow(
                BugFixWorkflow.run,
                BugWorkflowInput(
                    workflow_run_id=child_id,
                    product_id=inp.product_id,
                    product_name=inp.product_name,
                    repo_path=inp.repo_path,
                    jira_project_key=inp.jira_project_key,
                    ticket_id=inp.ticket_id,
                    title=inp.title,
                    description=inp.description,
                    risk_level=clf.risk_level,
                    auto_approve=clf.auto_approve,
                ),
                id=child_id,
                task_queue="projectzero-factory",
            )

        elif clf.workflow_type == "task":
            handle = await workflow.start_child_workflow(
                TaskWorkflow.run,
                TaskWorkflowInput(
                    workflow_run_id=child_id,
                    product_id=inp.product_id,
                    product_name=inp.product_name,
                    repo_path=inp.repo_path,
                    jira_project_key=inp.jira_project_key,
                    ticket_id=inp.ticket_id,
                    title=inp.title,
                    description=inp.description,
                ),
                id=child_id,
                task_queue="projectzero-factory",
            )

        else:
            # Default: story → FeatureDevelopmentWorkflow
            handle = await workflow.start_child_workflow(
                FeatureDevelopmentWorkflow.run,
                WorkflowInput(
                    workflow_run_id=child_id,
                    product_id=inp.product_id,
                    product_name=inp.product_name,
                    repo_path=inp.repo_path,
                    jira_project_key=inp.jira_project_key,
                    feature_id=inp.ticket_id,
                ),
                id=child_id,
                task_queue="projectzero-factory",
            )

        # Wait for child to complete
        result = await handle.result()
        self._stage = "completed"

        return {
            "ticket_id": inp.ticket_id,
            "classification": self._classification,
            "child_workflow_id": child_id,
            "result": result,
        }
