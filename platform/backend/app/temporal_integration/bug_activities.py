"""Bug Fix Activities.

Three activities for the BugFixWorkflow:
  diagnose_activity  → root cause analysis, reproduction steps, fix plan
  bugfix_activity    → patch implementation + regression test
  verify_activity    → verify fix, check no regressions
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


_DIAGNOSE_SYSTEM = """You are the Diagnose Agent for a software factory.

Given a bug report, produce a Markdown diagnosis document with:
1. Bug Summary (one paragraph, plain language)
2. Root Cause Analysis (technical, precise)
3. Reproduction Steps (numbered, exact)
4. Affected Components (files, services, functions)
5. Fix Plan (ordered steps — what to change and why)
6. Risk Assessment (what could go wrong with the fix)
7. Regression Risk (what other areas might break)

Be precise. No guessing. If uncertain, state it explicitly."""


_BUGFIX_SYSTEM = """You are the BugFix Agent for a software factory.

Given a diagnosis document, produce a Markdown fix document containing:
1. Fix Summary
2. Regression Test (full code — must fail before fix, pass after)
3. Patch Implementation (full code — minimal change, laser-focused on root cause)
4. Commit message (references ticket ID, describes fix not symptom)
5. Files changed (list with reason for each)

Rules:
- Minimal diff — fix the root cause only, no refactoring
- Regression test MUST be written before implementation
- No placeholder code"""


_VERIFY_SYSTEM = """You are the Verify Agent for a software factory.

Given a bug fix document, produce a Markdown verification report:
1. Verification Summary (PASS / FAIL)
2. Fix Correctness (does patch address root cause?)
3. Regression Test Result (expected: PASS)
4. Side Effect Check (any unintended changes?)
5. Remaining Risk (what could still go wrong?)
6. Recommendation (deploy / needs-rework / escalate)

Be rigorous. A PASS means you are confident in production safety."""


@activity.defn(name="diagnose_activity")
async def diagnose_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Diagnose Agent: analysing bug")
    brain_ctx = _brain_context(inp.product_id, inp.stage)

    user_prompt = f"""Product: {inp.product_name}
Bug Ticket: {inp.feature_id}
Repo: {inp.repo_path}

Bug context:
{json.dumps(inp.context, indent=2)}

Brain memory:
{brain_ctx}

Produce the root cause analysis and fix plan."""

    try:
        output = _call_claude(_DIAGNOSE_SYSTEM, user_prompt)
        rel = f".claude/bugs/{inp.feature_id}-diagnosis.md"
        path = _write_artifact(inp.repo_path, rel, output)
        activity.heartbeat("Diagnose Agent: diagnosis written")
        return AgentOutput(
            agent_type="diagnose",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Root cause identified for {inp.feature_id}",
        )
    except Exception as exc:
        logger.error("diagnose_activity failed: %s", exc)
        return AgentOutput(
            agent_type="diagnose", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


@activity.defn(name="bugfix_activity")
async def bugfix_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("BugFix Agent: implementing patch")

    diag_content = ""
    diag_path = inp.context.get("diagnosis_artifact_path", "")
    if diag_path and Path(diag_path).exists():
        diag_content = Path(diag_path).read_text(encoding="utf-8")[:4000]

    user_prompt = f"""Product: {inp.product_name}
Bug Ticket: {inp.feature_id}
Repo: {inp.repo_path}

Diagnosis:
{diag_content or '(not available — implement minimal safe fix)'}

Write regression test first, then patch implementation."""

    try:
        output = _call_claude(_BUGFIX_SYSTEM, user_prompt)
        rel = f".claude/bugs/{inp.feature_id}-fix.md"
        path = _write_artifact(inp.repo_path, rel, output)
        return AgentOutput(
            agent_type="bugfix",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Patch + regression test written for {inp.feature_id}",
        )
    except Exception as exc:
        return AgentOutput(
            agent_type="bugfix", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )


@activity.defn(name="verify_activity")
async def verify_activity(inp: AgentInput) -> AgentOutput:
    activity.heartbeat("Verify Agent: checking fix")

    fix_content = ""
    fix_path = inp.context.get("fix_artifact_path", "")
    if fix_path and Path(fix_path).exists():
        fix_content = Path(fix_path).read_text(encoding="utf-8")[:4000]

    user_prompt = f"""Product: {inp.product_name}
Bug Ticket: {inp.feature_id}

Fix document:
{fix_content or '(not available — perform conceptual verification)'}

Verify the fix is correct and safe to deploy."""

    try:
        output = _call_claude(_VERIFY_SYSTEM, user_prompt)
        rel = f".claude/bugs/{inp.feature_id}-verify.md"
        path = _write_artifact(inp.repo_path, rel, output)
        verdict = "PASS" if "PASS" in output[:500] else "FAIL"
        return AgentOutput(
            agent_type="verify",
            stage=inp.stage,
            status="completed",
            artifact_path=path,
            summary=f"Verification: {verdict} for {inp.feature_id}",
        )
    except Exception as exc:
        return AgentOutput(
            agent_type="verify", stage=inp.stage, status="failed",
            artifact_path="", summary="", error=str(exc),
        )
