"""Vision-to-PRD workflow: generates structured PRD + BMAD from raw product vision."""

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
class VisionInput:
    product_id: str
    vision_text: str
    created_by: str
    answers: dict = field(default_factory=dict)  # follow-up answers


STAGES = [
    "vision_intake",
    "structure_extraction",
    "gap_analysis",
    "prd_generation",
    "bmad_generation",
    "user_review",
    "store_and_handoff",
]


@workflow.defn
class VisionToPRDWorkflow:
    """Generate PRD + BMAD from raw vision text."""

    def __init__(self) -> None:
        self._current_stage = ""
        self._review_approved = False
        self._follow_up_answers: dict = {}
        self._generated_prd: Optional[str] = None
        self._generated_bmad: Optional[str] = None

    @workflow.signal
    async def provide_answers(self, answers: dict) -> None:
        """User provides follow-up answers for gaps."""
        self._follow_up_answers.update(answers)

    @workflow.signal
    async def approve_review(self) -> None:
        """User approves generated PRD + BMAD."""
        self._review_approved = True

    @workflow.query
    def current_stage(self) -> str:
        return self._current_stage

    @workflow.query
    def generated_prd(self) -> Optional[str]:
        return self._generated_prd

    @workflow.query
    def generated_bmad(self) -> Optional[str]:
        return self._generated_bmad

    @workflow.run
    async def run(self, input: VisionInput) -> dict:
        retry = RetryPolicy(maximum_attempts=3, backoff_coefficient=2.0)
        feature_id = f"vision-{input.product_id}"

        await workflow.execute_activity(
            sync_workflow_state,
            args=[feature_id, "started", "vision_intake"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        # Stage 1: Vision intake — parse raw text
        self._current_stage = "vision_intake"
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "vision_intake", "in_progress"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        intake_result = await workflow.execute_activity(
            execute_stage,
            args=[feature_id, "vision_intake", input.product_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry,
        )
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "vision_intake", "completed"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        # Stage 2: Structure extraction
        self._current_stage = "structure_extraction"
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "structure_extraction", "in_progress"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.execute_activity(
            execute_stage,
            args=[feature_id, "structure_extraction", input.product_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry,
        )
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "structure_extraction", "completed"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        # Stage 3: Gap analysis — may need follow-up
        self._current_stage = "gap_analysis"
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "gap_analysis", "in_progress"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        gap_result = await workflow.execute_activity(
            execute_stage,
            args=[feature_id, "gap_analysis", input.product_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry,
        )

        # If gaps found, wait for user answers (max 30 min)
        if gap_result.status == "needs_input":
            await workflow.execute_activity(
                request_approval,
                args=[feature_id, "gap_analysis_followup"],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry,
            )
            try:
                await workflow.wait_condition(
                    lambda: bool(self._follow_up_answers),
                    timeout=timedelta(minutes=30),
                )
            except TimeoutError:
                pass  # proceed with assumptions

        await workflow.execute_activity(
            record_step,
            args=[feature_id, "gap_analysis", "completed"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        # Stage 4: PRD generation
        self._current_stage = "prd_generation"
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "prd_generation", "in_progress"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.execute_activity(
            execute_stage,
            args=[feature_id, "prd_generation", input.product_id],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=retry,
        )
        prd_artifact = await workflow.execute_activity(
            generate_artifact,
            args=[feature_id, "prd_generation", "prd_document"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "prd_generation", "completed"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        # Stage 5: BMAD generation
        self._current_stage = "bmad_generation"
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "bmad_generation", "in_progress"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.execute_activity(
            execute_stage,
            args=[feature_id, "bmad_generation", input.product_id],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=retry,
        )
        bmad_artifact = await workflow.execute_activity(
            generate_artifact,
            args=[feature_id, "bmad_generation", "bmad_document"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.execute_activity(
            record_step,
            args=[feature_id, "bmad_generation", "completed"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        # Stage 6: User review — wait for approval
        self._current_stage = "user_review"
        await workflow.execute_activity(
            request_approval,
            args=[feature_id, "user_review"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        await workflow.wait_condition(lambda: self._review_approved)

        await workflow.execute_activity(
            record_step,
            args=[feature_id, "user_review", "completed"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        # Stage 7: Store and hand off
        self._current_stage = "store_and_handoff"
        await workflow.execute_activity(
            execute_stage,
            args=[feature_id, "store_and_handoff", input.product_id],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry,
        )

        await workflow.execute_activity(
            create_audit_log,
            args=[feature_id, "vision_to_prd_completed", {"product_id": input.product_id}],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        await workflow.execute_activity(
            sync_workflow_state,
            args=[feature_id, "completed", "store_and_handoff"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )

        return {
            "status": "completed",
            "prd_generated": True,
            "bmad_generated": True,
            "gaps_filled": bool(self._follow_up_answers),
        }
