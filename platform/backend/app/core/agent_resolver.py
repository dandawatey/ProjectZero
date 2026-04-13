"""agent_resolver.py — PRJ0-39.

STAGE_AGENT_MAP: maps workflow stage → Temporal activity config + agent metadata.
Single source of truth for stage→activity→agent_type wiring.

Activity names match @activity.defn names in temporal_integration/activities.py:
  spec_activity, arch_activity, impl_activity, review_activity, deploy_activity
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Map
# ---------------------------------------------------------------------------

STAGE_AGENT_MAP: dict[str, list[dict]] = {
    "specification": [
        {
            "activity": "spec_activity",
            "agent_type": "spec-agent",
            "task_queue": "factory-task-queue",
            "description": "Parse PRD/feature ticket → produce full specification doc",
        }
    ],
    "architecture": [
        {
            "activity": "arch_activity",
            "agent_type": "arch-agent",
            "task_queue": "factory-task-queue",
            "description": "Design system architecture → produce ADR + component/data/API docs",
        }
    ],
    "realization": [
        {
            "activity": "impl_activity",
            "agent_type": "impl-agent",
            "task_queue": "factory-task-queue",
            "description": "TDD implementation: write failing tests first, then implement",
        },
        {
            "activity": "review_activity",
            "agent_type": "review-agent",
            "task_queue": "factory-task-queue",
            "description": "Static analysis + code review → verdict APPROVED | CHANGES_REQUIRED | REJECTED",
        },
    ],
    "completion": [
        {
            "activity": "deploy_activity",
            "agent_type": "deploy-agent",
            "task_queue": "factory-task-queue",
            "description": "Prepare release artifacts: changelog, semver tag, deploy checklist, rollback plan",
        }
    ],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_agent(stage: str) -> list[dict]:
    """Return list of {activity, agent_type, task_queue, description} for stage.

    Args:
        stage: One of specification | architecture | realization | completion

    Returns:
        list[dict] — always a list (single-item for most stages, multi for realization)

    Raises:
        ValueError: unknown stage
    """
    stage = stage.strip().lower()
    if stage not in STAGE_AGENT_MAP:
        known = ", ".join(STAGE_AGENT_MAP.keys())
        raise ValueError(f"Unknown stage '{stage}'. Known: {known}")
    return STAGE_AGENT_MAP[stage]


def resolve_activity_name(stage: str, sub_step: int = 0) -> str:
    """Return Temporal activity function name for stage + sub_step index.

    Args:
        stage:    workflow stage name
        sub_step: index within the stage's activity list (default 0)

    Returns:
        str — e.g. "impl_activity"

    Raises:
        ValueError: unknown stage or sub_step out of range
    """
    agents = resolve_agent(stage)
    if sub_step < 0 or sub_step >= len(agents):
        raise ValueError(
            f"sub_step {sub_step} out of range for stage '{stage}' "
            f"(has {len(agents)} activities)"
        )
    return agents[sub_step]["activity"]


def agent_type_for_contribution(stage: str, sub_step: int = 0) -> str:
    """Return agent_type string for AgentContribution records.

    Args:
        stage:    workflow stage name
        sub_step: index within stage's activity list (default 0)

    Returns:
        str — e.g. "spec-agent", "impl-agent", "review-agent"

    Raises:
        ValueError: unknown stage or sub_step out of range
    """
    agents = resolve_agent(stage)
    if sub_step < 0 or sub_step >= len(agents):
        raise ValueError(
            f"sub_step {sub_step} out of range for stage '{stage}' "
            f"(has {len(agents)} activities)"
        )
    return agents[sub_step]["agent_type"]


def all_stages() -> list[str]:
    """Return ordered list of all known stages."""
    return list(STAGE_AGENT_MAP.keys())
