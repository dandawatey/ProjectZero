"""Factory-specific Temporal activities — dogfood pipeline for PRJ0 tickets.

Factory activities mirror the product activities in activities.py but are
aware of the factory codebase: FastAPI + React + Postgres + Temporal + Anthropic.

Activity map:
  factory_spec_activity     → reads PRJ0 JIRA ticket, produces factory-scoped spec
  factory_arch_activity     → ADR in docs/adr/, aware of existing factory architecture
  factory_impl_activity     → TDD impl plan, pytest + 80% coverage enforced
  factory_review_activity   → reviews against factory governance (MCRA, no-ticket-no-work)
  factory_deploy_activity   → PR + CHANGELOG entry for factory repo
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from temporalio import activity

# Re-export shared types so importers can grab from one place
from app.temporal_integration.activities import (  # noqa: F401
    AgentInput,
    AgentOutput,
    _call_claude,
    _write_artifact,
    _brain_context,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Factory system-prompt context block (injected into every factory activity)
# ---------------------------------------------------------------------------

_FACTORY_STACK = """
## Factory Codebase Context

Stack:
- Backend: FastAPI (Python 3.12) — platform/backend/
- Frontend: React 18 + TypeScript + Vite — platform/frontend/
- Database: PostgreSQL via SQLAlchemy async (asyncpg)
- Workflow engine: Temporal.io (temporalio SDK)
- AI layer: Anthropic Claude API (anthropic SDK)
- Testing: pytest + pytest-asyncio; coverage threshold 80%
- Linting: ruff; type checking: mypy (strict mode)

Key modules:
- app/temporal_integration/  — workflows, activities, worker, client
- app/api/routes/            — FastAPI routers (one file per domain)
- app/models/                — SQLAlchemy ORM models
- app/services/              — business logic / third-party clients
- app/core/                  — config, database, middleware, agent_resolver

Governance rules (non-negotiable):
- Every change must reference a PRJ0 JIRA ticket
- TDD: failing test FIRST, then implementation
- Coverage >= 80%
- MCRA: Maker-Checker-Reviewer-Approver on significant changes
- No silent mutations — every change visible in git history
- Stage gates sequential: Spec → Arch → Impl → Review → Deploy
"""


# ---------------------------------------------------------------------------
# Activity: Factory Spec Agent
# ---------------------------------------------------------------------------

_FACTORY_SPEC_SYSTEM = f"""You are the Factory Spec Agent for ProjectZeroFactory.
Your role: read a PRJ0 JIRA ticket and produce a complete specification scoped to
the factory codebase and governance model.

{_FACTORY_STACK}

Output a Markdown document with:
1. Feature Overview (problem, goal, success metrics)
2. User Stories (As a <role>, I want <action>, so that <benefit>)
3. Acceptance Criteria (Given/When/Then, ≥3 per story)
4. SPARC Definition of Done (Spec / Pseudocode / Arch / Refinement / Completion)
5. Factory impact (which modules are touched, which governance rules apply)
6. Dependencies and risks specific to the factory stack

Be precise. No vague language. Every AC must be testable."""


@activity.defn(name="factory_spec_activity")
async def factory_spec_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Factory Spec Agent: reading Brain memories")
    brain_ctx = _brain_context(inp.product_id, inp.stage)

    user_prompt = f"""Factory: ProjectZeroFactory
PRJ0 Ticket: {inp.feature_id}
Project Key: {inp.jira_project_key}
Repo: {inp.repo_path}

Prior context from Brain:
{brain_ctx}

Additional context: {json.dumps(inp.context)}

Produce the full factory specification document for this PRJ0 ticket.
Scope every decision to the factory stack (FastAPI/React/Postgres/Temporal/Anthropic)."""

    activity.heartbeat("Factory Spec Agent: calling Claude")
    try:
        output = _call_claude(_FACTORY_SPEC_SYSTEM, user_prompt)
        rel = f".claude/specs/{inp.feature_id}-factory-spec.md"
        path = _write_artifact(inp.repo_path, rel, output)
        activity.heartbeat("Factory Spec Agent: artifact written")
        return AgentOutput(
            agent_type="factory-spec",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Factory spec written for {inp.feature_id} — {len(output)} chars",
        )
    except Exception as exc:
        logger.error("factory_spec_activity failed: %s", exc)
        return AgentOutput(
            agent_type="factory-spec", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


# ---------------------------------------------------------------------------
# Activity: Factory Arch Agent
# ---------------------------------------------------------------------------

_FACTORY_ARCH_SYSTEM = f"""You are the Factory Arch Agent for ProjectZeroFactory.
Your role: design or extend the factory architecture for a PRJ0 feature.

{_FACTORY_STACK}

Output a Markdown ADR document with:
1. ADR header: title, status (Proposed), date, context, decision, consequences
2. Component diagram (Mermaid preferred) showing affected factory modules
3. Data model changes (SQLAlchemy models, migration notes)
4. API contract changes (new/modified endpoints, request/response shapes)
5. Temporal workflow/activity changes (if any)
6. Technology choices with rationale — justify every deviation from existing stack
7. Security considerations (auth, input validation, secrets handling)
8. Scalability and observability (logging, metrics, health checks)
9. Test strategy (unit / integration / e2e, which pytest fixtures needed)

Every decision must have a rationale. Rejected alternatives must be noted."""


@activity.defn(name="factory_arch_activity")
async def factory_arch_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Factory Arch Agent: reading spec + Brain")
    brain_ctx = _brain_context(inp.product_id, inp.stage)

    spec_content = ""
    spec_path = inp.context.get("spec_artifact_path", "")
    if spec_path and Path(spec_path).exists():
        spec_content = Path(spec_path).read_text(encoding="utf-8")[:3000]

    user_prompt = f"""Factory: ProjectZeroFactory
Ticket: {inp.feature_id}
Repo: {inp.repo_path}

Specification:
{spec_content or "(not available — design based on ticket ID)"}

Brain context:
{brain_ctx}

Produce the factory ADR. Output path will be docs/adr/{inp.feature_id}-factory-adr.md.
Ensure architecture is consistent with existing factory modules."""

    activity.heartbeat("Factory Arch Agent: calling Claude")
    try:
        output = _call_claude(_FACTORY_ARCH_SYSTEM, user_prompt)
        rel = f"docs/adr/{inp.feature_id}-factory-adr.md"
        path = _write_artifact(inp.repo_path, rel, output)
        return AgentOutput(
            agent_type="factory-arch",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Factory ADR written for {inp.feature_id}",
        )
    except Exception as exc:
        logger.error("factory_arch_activity failed: %s", exc)
        return AgentOutput(
            agent_type="factory-arch", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


# ---------------------------------------------------------------------------
# Activity: Factory Impl Agent
# ---------------------------------------------------------------------------

_FACTORY_IMPL_SYSTEM = f"""You are the Factory Impl Agent for ProjectZeroFactory.
Your role: produce a TDD implementation plan for a PRJ0 factory feature.

{_FACTORY_STACK}

Output a Markdown document containing:
1. Implementation plan (ordered steps, each referencing a test)
2. Test file(s) (full pytest code — failing tests written FIRST)
   - Use pytest-asyncio for async routes/services
   - Mock external deps (Temporal, JIRA, Anthropic, Confluence)
   - Target >= 80% branch coverage for changed modules
3. Implementation file(s) (full code that makes tests pass)
4. Migration script (if DB schema changes)
5. Commit message(s) referencing {"{ticket_id}"}
6. Coverage report plan (which lines/branches are covered)

Rules:
- Write the FAILING test first, then the implementation — no exceptions
- No placeholder code — complete, runnable code only
- Follow ruff + mypy strict conventions
- No new dependencies without explicit justification"""


@activity.defn(name="factory_impl_activity")
async def factory_impl_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Factory Impl Agent: reading arch + Brain")
    brain_ctx = _brain_context(inp.product_id, inp.stage)

    arch_content = ""
    arch_path = inp.context.get("arch_artifact_path", "")
    if arch_path and Path(arch_path).exists():
        arch_content = Path(arch_path).read_text(encoding="utf-8")[:3000]

    user_prompt = f"""Factory: ProjectZeroFactory
Ticket: {inp.feature_id}
Repo: {inp.repo_path}

Architecture:
{arch_content or "(not available)"}

Brain context:
{brain_ctx}

Implement this factory feature following strict TDD.
Output pytest tests first (they must fail before impl), then the implementation.
All code must conform to ruff + mypy strict."""

    activity.heartbeat("Factory Impl Agent: calling Claude")
    try:
        output = _call_claude(
            _FACTORY_IMPL_SYSTEM.replace("{ticket_id}", inp.feature_id),
            user_prompt,
        )
        rel = f".claude/impl/{inp.feature_id}-factory-impl.md"
        path = _write_artifact(inp.repo_path, rel, output)
        return AgentOutput(
            agent_type="factory-impl",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Factory TDD impl plan written for {inp.feature_id}",
        )
    except Exception as exc:
        logger.error("factory_impl_activity failed: %s", exc)
        return AgentOutput(
            agent_type="factory-impl", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


# ---------------------------------------------------------------------------
# Activity: Factory Review Agent
# ---------------------------------------------------------------------------

_FACTORY_REVIEW_SYSTEM = f"""You are the Factory Review Agent for ProjectZeroFactory.
Your role: review an implementation against factory governance rules.

{_FACTORY_STACK}

Governance checklist (every item must be verified):
- MCRA: Maker-Checker-Reviewer-Approver — four-eye principle on all significant changes
- No Ticket No Work — every commit references a PRJ0 ticket
- TDD — tests written before implementation (verify test file timestamps / ordering)
- Coverage >= 80% — coverage report must be present
- No silent mutations — all changes documented
- Stage gates — work must trace through Spec → Arch → Impl
- No secrets in code — no hardcoded API keys, passwords, or tokens
- ruff + mypy — zero lint/type errors
- No new dependencies without ADR rationale

Output a Markdown document with:
1. Review verdict (APPROVED / CHANGES_REQUIRED / REJECTED)
2. Governance compliance matrix (each rule: PASS / FAIL / WARNING)
3. Critical issues (blocking — must fix before merge)
4. Major issues (should fix)
5. Minor issues (suggestions)
6. Security findings
7. Coverage gaps
8. Summary recommendation

Be direct. Flag every violation. Apply factory rules strictly."""


@activity.defn(name="factory_review_activity")
async def factory_review_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Factory Review Agent: reading impl artifact")

    impl_content = ""
    impl_path = inp.context.get("impl_artifact_path", "")
    if impl_path and Path(impl_path).exists():
        impl_content = Path(impl_path).read_text(encoding="utf-8")[:4000]

    user_prompt = f"""Factory: ProjectZeroFactory
Ticket: {inp.feature_id}

Implementation artifact:
{impl_content or "(not available — perform governance review based on ticket)"}

Apply the full factory governance checklist.
Flag every MCRA / TDD / coverage / no-ticket-no-work violation."""

    activity.heartbeat("Factory Review Agent: calling Claude")
    try:
        output = _call_claude(_FACTORY_REVIEW_SYSTEM, user_prompt)
        rel = f".claude/reviews/{inp.feature_id}-factory-review.md"
        path = _write_artifact(inp.repo_path, rel, output)
        verdict = "APPROVED" if "APPROVED" in output[:500] else "CHANGES_REQUIRED"
        return AgentOutput(
            agent_type="factory-review",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Factory governance review: {verdict} for {inp.feature_id}",
        )
    except Exception as exc:
        logger.error("factory_review_activity failed: %s", exc)
        return AgentOutput(
            agent_type="factory-review", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


# ---------------------------------------------------------------------------
# Activity: Factory Deploy Agent
# ---------------------------------------------------------------------------

_FACTORY_DEPLOY_SYSTEM = f"""You are the Factory Deploy Agent for ProjectZeroFactory.
Your role: prepare PR and release artifacts for a completed factory feature.

{_FACTORY_STACK}

Output a Markdown document with:
1. Pull Request description
   - Title (≤72 chars, references PRJ0 ticket)
   - Summary (what changed and why)
   - Test plan (what to verify manually after merge)
   - Checklist (tests pass, coverage ≥80%, ruff clean, mypy clean, JIRA updated)
2. CHANGELOG entry (Keep a Changelog format — Added / Changed / Fixed / Removed)
3. Release tag recommendation (semver — patch for bugfix, minor for feature, major for breaking)
4. Factory deployment checklist
   - Pre-merge: CI passes, coverage gate met, review approved
   - Post-merge: Temporal worker restarted if new workflow/activity registered
   - DB migration applied if schema changed
   - Memory recorded in Brain
5. Rollback plan
6. Stakeholder notification draft (Slack / email)

Be precise about semver bump reasoning."""


@activity.defn(name="factory_deploy_activity")
async def factory_deploy_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Factory Deploy Agent: preparing PR + release artifacts")

    review_content = ""
    review_path = inp.context.get("review_artifact_path", "")
    if review_path and Path(review_path).exists():
        review_content = Path(review_path).read_text(encoding="utf-8")[:2000]

    user_prompt = f"""Factory: ProjectZeroFactory
Ticket: {inp.feature_id}
JIRA Project: {inp.jira_project_key}

Review summary:
{review_content or "(review approved — no issues)"}

Prepare PR description and CHANGELOG entry for this factory feature.
Include Temporal worker restart note if new workflow/activity was registered."""

    activity.heartbeat("Factory Deploy Agent: calling Claude")
    try:
        output = _call_claude(_FACTORY_DEPLOY_SYSTEM, user_prompt)
        rel = f".claude/releases/{inp.feature_id}-factory-release.md"
        path = _write_artifact(inp.repo_path, rel, output)
        return AgentOutput(
            agent_type="factory-deploy",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Factory PR + release artifacts ready for {inp.feature_id}",
        )
    except Exception as exc:
        logger.error("factory_deploy_activity failed: %s", exc)
        return AgentOutput(
            agent_type="factory-deploy", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )
