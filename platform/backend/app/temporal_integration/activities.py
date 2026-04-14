"""Temporal activity implementations — PRJ0-43 / PRJ0-44.

Each activity = one agent persona. Calls Claude API, reads Brain, writes
artifact to product repo_path, records AgentContribution.

Activity map:
  spec_activity     → Spec Agent    (specification stage)
  arch_activity     → Arch Agent    (architecture stage)
  impl_activity     → Impl Agent    (realization stage)
  review_activity   → Review Agent  (realization stage, after impl)
  deploy_activity   → Deploy Agent  (completion stage)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from temporalio import activity

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared input/output types
# ---------------------------------------------------------------------------

@dataclass
class AgentInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    repo_path: str
    jira_project_key: str
    feature_id: str          # JIRA ticket ID being worked on
    stage: str               # specification | architecture | realization | completion
    context: dict            # extra context (prior artifact paths, brain memories)


@dataclass
class AgentOutput:
    agent_type: str
    stage: str
    status: str              # completed | failed
    artifact_path: str       # path written inside repo_path
    summary: str             # ≤300 chars — what was done
    error: str | None = None


# ---------------------------------------------------------------------------
# Claude API helper
# ---------------------------------------------------------------------------

def _call_claude(system: str, user: str, model: str | None = None) -> str:
    """Call Anthropic Claude synchronously (activities run in thread executor)."""
    try:
        import anthropic  # type: ignore[import-untyped]
    except ImportError:
        raise RuntimeError("anthropic package not installed — run: uv pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")

    client = anthropic.Anthropic(api_key=api_key)
    chosen_model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    message = client.messages.create(
        model=chosen_model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text


def _write_artifact(repo_path: str, rel_path: str, content: str) -> str:
    """Write content to repo_path/rel_path, return absolute path."""
    target = Path(repo_path) / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return str(target)


def _brain_context(product_id: str, stage: str) -> str:
    """Fetch Brain memories for this product+stage. Returns formatted string."""
    import httpx  # type: ignore[import-untyped]
    try:
        base = os.getenv("API_BASE_URL", "http://localhost:8000")
        r = httpx.get(
            f"{base}/api/v1/brain/memories",
            params={"scope": "product", "product_id": product_id, "limit": 10},
            timeout=10,
        )
        if r.status_code == 200:
            memories = r.json()
            return "\n".join(f"- {m.get('content', '')}" for m in memories[:10])
    except Exception as exc:
        logger.warning("Brain fetch failed: %s", exc)
    return "(no prior memories)"


# ---------------------------------------------------------------------------
# Activity: Spec Agent
# ---------------------------------------------------------------------------

@activity.defn(name="spec_activity")
async def spec_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Spec Agent: reading Brain memories")
    brain_ctx = _brain_context(inp.product_id, inp.stage)

    user_prompt = f"""Product: {inp.product_name}
JIRA Feature: {inp.feature_id}
Project Key: {inp.jira_project_key}
Repo: {inp.repo_path}

Prior context from Brain:
{brain_ctx}

Additional context: {json.dumps(inp.context)}

Produce the full specification document for this feature."""

    activity.heartbeat("Spec Agent: calling Claude")
    try:
        from app.services.agent_dispatcher import AgentDispatcher
        dispatcher = AgentDispatcher()
        output = dispatcher.run(
            skill_id="spec",
            product_id=inp.product_id,
            feature_id=inp.feature_id,
            context_str=user_prompt,
            repo_path=inp.repo_path,
        )
        rel = f".claude/specs/{inp.feature_id}-spec.md"
        path = _write_artifact(inp.repo_path, rel, output)
        activity.heartbeat("Spec Agent: artifact written")
        return AgentOutput(
            agent_type="spec",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Spec written for {inp.feature_id} — {len(output)} chars",
        )
    except Exception as exc:
        logger.error("spec_activity failed: %s", exc)
        return AgentOutput(
            agent_type="spec", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


# ---------------------------------------------------------------------------
# Activity: Arch Agent
# ---------------------------------------------------------------------------

@activity.defn(name="arch_activity")
async def arch_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Arch Agent: reading spec + Brain")
    brain_ctx = _brain_context(inp.product_id, inp.stage)

    # Read prior spec artifact if available
    spec_content = ""
    spec_path = inp.context.get("spec_artifact_path", "")
    if spec_path and Path(spec_path).exists():
        spec_content = Path(spec_path).read_text(encoding="utf-8")[:3000]

    user_prompt = f"""Product: {inp.product_name}
Feature: {inp.feature_id}
Repo: {inp.repo_path}

Specification:
{spec_content or '(not available — design based on feature ID)'}

Brain context:
{brain_ctx}

Produce the architecture document."""

    activity.heartbeat("Arch Agent: calling Claude")
    try:
        from app.services.agent_dispatcher import AgentDispatcher
        dispatcher = AgentDispatcher()
        output = dispatcher.run(
            skill_id="arch",
            product_id=inp.product_id,
            feature_id=inp.feature_id,
            context_str=user_prompt,
            repo_path=inp.repo_path,
        )
        rel = f"docs/adr/{inp.feature_id}-adr.md"
        path = _write_artifact(inp.repo_path, rel, output)
        return AgentOutput(
            agent_type="arch", stage=inp.stage, status="completed",
            artifact_path=path,
            summary=f"ADR written for {inp.feature_id}",
        )
    except Exception as exc:
        return AgentOutput(
            agent_type="arch", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


# ---------------------------------------------------------------------------
# Activity: Impl Agent
# ---------------------------------------------------------------------------

@activity.defn(name="impl_activity")
async def impl_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Impl Agent: reading arch + Brain")
    brain_ctx = _brain_context(inp.product_id, inp.stage)

    arch_content = ""
    arch_path = inp.context.get("arch_artifact_path", "")
    if arch_path and Path(arch_path).exists():
        arch_content = Path(arch_path).read_text(encoding="utf-8")[:3000]

    user_prompt = f"""Product: {inp.product_name}
Feature: {inp.feature_id}
Repo: {inp.repo_path}

Architecture:
{arch_content or '(not available)'}

Brain context:
{brain_ctx}

Implement this feature following TDD. Output tests first, then implementation."""

    activity.heartbeat("Impl Agent: calling Claude")
    try:
        from app.services.agent_dispatcher import AgentDispatcher
        dispatcher = AgentDispatcher()
        output = dispatcher.run(
            skill_id="implement",
            product_id=inp.product_id,
            feature_id=inp.feature_id,
            context_str=user_prompt,
            repo_path=inp.repo_path,
        )
        rel = f".claude/impl/{inp.feature_id}-impl.md"
        path = _write_artifact(inp.repo_path, rel, output)
        return AgentOutput(
            agent_type="impl", stage=inp.stage, status="completed",
            artifact_path=path,
            summary=f"TDD impl plan written for {inp.feature_id}",
        )
    except Exception as exc:
        return AgentOutput(
            agent_type="impl", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


# ---------------------------------------------------------------------------
# Activity: Review Agent
# ---------------------------------------------------------------------------

@activity.defn(name="review_activity")
async def review_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Review Agent: reading impl artifact")

    impl_content = ""
    impl_path = inp.context.get("impl_artifact_path", "")
    if impl_path and Path(impl_path).exists():
        impl_content = Path(impl_path).read_text(encoding="utf-8")[:4000]

    user_prompt = f"""Product: {inp.product_name}
Feature: {inp.feature_id}

Implementation artifact:
{impl_content or '(not available — perform conceptual review)'}

Perform thorough code review."""

    activity.heartbeat("Review Agent: calling Claude")
    try:
        from app.services.agent_dispatcher import AgentDispatcher
        dispatcher = AgentDispatcher()
        output = dispatcher.run(
            skill_id="review",
            product_id=inp.product_id,
            feature_id=inp.feature_id,
            context_str=user_prompt,
            repo_path=inp.repo_path,
        )
        rel = f".claude/reviews/{inp.feature_id}-review.md"
        path = _write_artifact(inp.repo_path, rel, output)
        verdict = "APPROVED" if "APPROVED" in output[:500] else "CHANGES_REQUIRED"
        return AgentOutput(
            agent_type="review", stage=inp.stage, status="completed",
            artifact_path=path,
            summary=f"Review: {verdict} for {inp.feature_id}",
        )
    except Exception as exc:
        return AgentOutput(
            agent_type="review", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


# ---------------------------------------------------------------------------
# Activity: Deploy Agent
# ---------------------------------------------------------------------------

@activity.defn(name="deploy_activity")
async def deploy_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Deploy Agent: preparing release")

    review_content = ""
    review_path = inp.context.get("review_artifact_path", "")
    if review_path and Path(review_path).exists():
        review_content = Path(review_path).read_text(encoding="utf-8")[:2000]

    user_prompt = f"""Product: {inp.product_name}
Feature: {inp.feature_id}
JIRA Project: {inp.jira_project_key}

Review summary:
{review_content or '(review approved)'}

Prepare release artifacts."""

    activity.heartbeat("Deploy Agent: calling Claude")
    try:
        from app.services.agent_dispatcher import AgentDispatcher
        dispatcher = AgentDispatcher()
        output = dispatcher.run(
            skill_id="deploy",
            product_id=inp.product_id,
            feature_id=inp.feature_id,
            context_str=user_prompt,
            repo_path=inp.repo_path,
        )
        rel = f".claude/releases/{inp.feature_id}-release.md"
        path = _write_artifact(inp.repo_path, rel, output)
        return AgentOutput(
            agent_type="deploy", stage=inp.stage, status="completed",
            artifact_path=path,
            summary=f"Release artifact ready for {inp.feature_id}",
        )
    except Exception as exc:
        return AgentOutput(
            agent_type="deploy", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )
