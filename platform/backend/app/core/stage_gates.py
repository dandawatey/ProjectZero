"""Stage gate enforcement for ProjectZeroFactory workflows.

Enforces specification → architecture → realization → completion ordering.
No stage may be skipped.
"""

from __future__ import annotations

STAGE_ORDER = ["specification", "architecture", "realization", "completion"]

_TERMINAL = frozenset({"completed", "failed"})


class StageGateError(Exception):
    """Raised when a requested stage transition violates ordering rules."""


def validate_stage_transition(current_stage: str | None, requested_stage: str) -> None:
    """Raise StageGateError if requested_stage skips a stage.

    Rules:
    - None / "pending" → only "specification" allowed
    - Each stage can only advance to the immediately next stage in STAGE_ORDER
    - Terminal states ("completed", "failed") cannot transition further
    - Requesting a stage already completed (going backwards) is also rejected
    """
    if requested_stage in _TERMINAL:
        # Terminal states are set by the engine, not stage-gate advance logic.
        # Allow them through — they don't represent a stage skip.
        return

    if requested_stage not in STAGE_ORDER:
        raise StageGateError(
            f"Unknown stage '{requested_stage}'. Valid stages: {STAGE_ORDER}"
        )

    if current_stage in _TERMINAL:
        raise StageGateError(
            f"Workflow is in terminal state '{current_stage}'. No further stage transitions allowed."
        )

    if current_stage is None or current_stage == "pending":
        # First transition: must be specification
        if requested_stage != STAGE_ORDER[0]:
            raise StageGateError(
                f"Workflow not yet started. First stage must be '{STAGE_ORDER[0]}', "
                f"got '{requested_stage}'."
            )
        return

    if current_stage not in STAGE_ORDER:
        raise StageGateError(
            f"Current stage '{current_stage}' is not a recognised stage. Cannot advance."
        )

    current_idx = STAGE_ORDER.index(current_stage)
    requested_idx = STAGE_ORDER.index(requested_stage)

    if requested_idx != current_idx + 1:
        if requested_idx <= current_idx:
            raise StageGateError(
                f"Cannot go backwards from '{current_stage}' to '{requested_stage}'."
            )
        skipped = STAGE_ORDER[current_idx + 1 : requested_idx]
        raise StageGateError(
            f"Cannot skip from '{current_stage}' to '{requested_stage}'. "
            f"Stage(s) skipped: {skipped}."
        )


def next_stage(current: str) -> str | None:
    """Return next stage name, or None if at completion or in terminal state."""
    if current in _TERMINAL or current not in STAGE_ORDER:
        return None
    idx = STAGE_ORDER.index(current)
    if idx + 1 >= len(STAGE_ORDER):
        return None
    return STAGE_ORDER[idx + 1]


def is_terminal(stage: str) -> bool:
    """Return True for completed / failed."""
    return stage in _TERMINAL
