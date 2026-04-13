"""Business documents workflow: generates full business doc suite in two phases."""

from datetime import timedelta
from dataclasses import dataclass, field
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
        request_approval,
    )


@dataclass
class BusinessDocsInput:
    product_id: str
    phase: str  # "discovery" or "planning"
    created_by: str
    context: dict = field(default_factory=dict)


DISCOVERY_STAGES = [
    "tam_sam_som",
    "competitive_analysis",
    "team_composition",
    "business_model",
]

PLANNING_STAGES = [
    "financial_projections",
    "build_run_costing",
    "gtm_strategy",
    "pitch_deck",
    "investor_data_room",
]


@workflow.defn
class BusinessDocsWorkflow:
    """Generate business documents — Phase 1 (discovery) or Phase 2 (planning)."""

    def __init__(self) -> None:
        self._current_stage = ""
        self._doc_approved = False

    @workflow.signal
    async def approve_doc(self) -> None:
        self._doc_approved = True

    @workflow.query
    def current_stage(self) -> str:
        return self._current_stage

    @workflow.run
    async def run(self, input: BusinessDocsInput) -> dict:
        retry = RetryPolicy(maximum_attempts=3, backoff_coefficient=2.0)
        feature_id = f"bizdocs-{input.phase}-{input.product_id}"
        stages = DISCOVERY_STAGES if input.phase == "discovery" else PLANNING_STAGES

        await workflow.execute_activity(
            sync_workflow_state,
            args=[feature_id, "started", stages[0]],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        results = []
        for stage in stages:
            self._current_stage = stage
            self._doc_approved = False

            # Execute document generation
            await workflow.execute_activity(
                record_step,
                args=[feature_id, stage, "in_progress"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry,
            )

            result = await workflow.execute_activity(
                execute_stage,
                args=[feature_id, stage, input.product_id],
                start_to_close_timeout=timedelta(minutes=15),
                retry_policy=retry,
            )

            # Generate artifact
            await workflow.execute_activity(
                generate_artifact,
                args=[feature_id, stage, f"{stage}_document"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry,
            )

            # User review per document
            await workflow.execute_activity(
                request_approval,
                args=[feature_id, f"{stage}_review"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry,
            )
            await workflow.wait_condition(lambda: self._doc_approved)

            await workflow.execute_activity(
                record_step,
                args=[feature_id, stage, "completed"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry,
            )

            results.append({"stage": stage, "status": "completed"})

        await workflow.execute_activity(
            sync_workflow_state,
            args=[feature_id, "completed", stages[-1]],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        return {
            "status": "completed",
            "phase": input.phase,
            "documents_generated": len(results),
            "results": results,
        }
