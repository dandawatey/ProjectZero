"""Task Activities.

Two activities for TaskWorkflow (chores, docs, config, dependency bumps):
  task_impl_activity    → execute the task, produce implementation notes
  task_review_activity  → quick sanity check, no blocking gates
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from temporalio import activity

from app.temporal_integration.activities import (
    AgentInput,
    AgentOutput,
    _call_claude,
    _write_artifact,
    _brain_context,
)

logger = logging.getLogger(__name__)


_TASK_IMPL_SYSTEM = """You are the Task Agent for a software factory.

Given a task ticket (chore, docs update, config change, dependency bump),
produce a Markdown implementation document with:
1. Task Summary
2. Changes Made (specific files and what changed)
3. Commands Run (if any — e.g. npm update, alembic revision)
4. Verification Steps (how to confirm task is complete)
5. Commit message (references ticket)

Keep it concise. Tasks are simple by definition."""


_TASK_REVIEW_SYSTEM = """You are the Task Reviewer for a software factory.

Perform a quick sanity check on a completed task:
1. Verdict: LOOKS GOOD | MINOR ISSUES | BLOCKED
2. Correctness (did it accomplish what the ticket asked?)
3. Side effects (anything unexpected?)
4. Recommendation

This is a lightweight review — no deep analysis needed for routine tasks."""


@activity.defn(name="task_impl_activity")
async def task_impl_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Task Agent: executing task")
    brain_ctx = _brain_context(inp.product_id, inp.stage)

    user_prompt = f"""Product: {inp.product_name}
Task Ticket: {inp.feature_id}
Repo: {inp.repo_path}

Task context:
{json.dumps(inp.context, indent=2)}

Brain memory:
{brain_ctx}

Execute this task and document what was done."""

    try:
        output = _call_claude(_TASK_IMPL_SYSTEM, user_prompt)
        rel = f".claude/tasks/{inp.feature_id}-task.md"
        path = _write_artifact(inp.repo_path, rel, output)
        activity.heartbeat("Task Agent: task completed")
        return AgentOutput(
            agent_type="task",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Task {inp.feature_id} executed",
        )
    except Exception as exc:
        logger.error("task_impl_activity failed: %s", exc)
        return AgentOutput(
            agent_type="task", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


@activity.defn(name="task_review_activity")
async def task_review_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Task Reviewer: sanity check")

    impl_content = ""
    impl_path = inp.context.get("impl_artifact_path", "")
    if impl_path and Path(impl_path).exists():
        impl_content = Path(impl_path).read_text(encoding="utf-8")[:2000]

    user_prompt = f"""Product: {inp.product_name}
Task Ticket: {inp.feature_id}

Implementation notes:
{impl_content or '(not available)'}

Quick sanity check — is this task complete and safe?"""

    try:
        output = _call_claude(_TASK_REVIEW_SYSTEM, user_prompt)
        rel = f".claude/tasks/{inp.feature_id}-review.md"
        path = _write_artifact(inp.repo_path, rel, output)
        verdict = "LOOKS GOOD" if "LOOKS GOOD" in output[:300] else "REVIEWED"
        return AgentOutput(
            agent_type="task-review",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Task review: {verdict} for {inp.feature_id}",
        )
    except Exception as exc:
        return AgentOutput(
            agent_type="task-review", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )
