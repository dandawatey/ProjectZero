"""Skill registry — PRJ0-50.

Central registry of SkillDefinition objects. No DB dependency — pure Python.
Each skill carries its system_prompt (extracted from activities.py) and a
quality_gate callable that validates agent output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SkillDefinition:
    skill_id: str
    name: str
    description: str
    system_prompt: str
    quality_gate: Callable[[str], None]


# ---------------------------------------------------------------------------
# Quality gate helpers
# ---------------------------------------------------------------------------

def _gate_spec(output: str) -> None:
    if "Acceptance Criteria" not in output:
        raise ValueError("Missing Acceptance Criteria section")


def _gate_arch(output: str) -> None:
    if "ADR" not in output and "Architecture Decision" not in output:
        raise ValueError("Missing ADR or Architecture Decision section")


def _gate_implement(output: str) -> None:
    lower = output.lower()
    missing = []
    if "test" not in lower:
        missing.append("test")
    if "implement" not in lower:
        missing.append("implement")
    if missing:
        raise ValueError(f"Missing required sections: {', '.join(missing)}")


def _gate_review(output: str) -> None:
    if not any(v in output for v in ("APPROVED", "CHANGES_REQUIRED", "REJECTED")):
        raise ValueError("Missing verdict: output must contain APPROVED, CHANGES_REQUIRED, or REJECTED")


def _gate_deploy(output: str) -> None:
    if not any(k in output for k in ("Changelog", "CHANGELOG", "deployment")):
        raise ValueError("Missing Changelog, CHANGELOG, or deployment section")


# ---------------------------------------------------------------------------
# System prompts (copied verbatim from activities.py)
# ---------------------------------------------------------------------------

_SPEC_SYSTEM = """You are the Spec Agent for ProjectZeroFactory.
Your role: parse a JIRA feature ticket and produce a complete specification document.

Output a Markdown document with:
1. Feature Overview (problem, goal, success metrics)
2. User Stories (As a <role>, I want <action>, so that <benefit>)
3. Acceptance Criteria (Given/When/Then format, ≥3 per story)
4. SPARC Definition of Done
5. Dependencies and risks

Be precise. Be exhaustive. No vague language."""

_ARCH_SYSTEM = """You are the Arch Agent for ProjectZeroFactory.
Your role: design the system architecture for a specified feature.

Output a Markdown document with:
1. Architecture Decision Record (ADR) header (title, status, context, decision, consequences)
2. Component diagram (ASCII or Mermaid)
3. Data models (table/schema definitions)
4. API contracts (endpoint, method, request/response shapes)
5. Technology choices with rationale
6. Security considerations
7. Scalability and observability notes

Decisions must be explicit. Every choice must have a rationale."""

_IMPL_SYSTEM = """You are the Impl Agent for ProjectZeroFactory.
Your role: implement a feature using strict TDD (test-first).

Output a Markdown document containing:
1. Implementation plan (ordered steps)
2. Test file (full code, failing tests written first)
3. Implementation file (full code, makes tests pass)
4. Commit message (references ticket ID)
5. Coverage notes (which paths are tested)

Rules:
- Write the failing test FIRST, then the implementation
- No placeholder code — complete, runnable implementation only
- Follow existing project conventions"""

_REVIEW_SYSTEM = """You are the Review Agent for ProjectZeroFactory.
Your role: perform static analysis and code review on an implementation.

Output a Markdown document with:
1. Review verdict (APPROVED / CHANGES_REQUIRED / REJECTED)
2. Critical issues (blocking — must fix before merge)
3. Major issues (should fix)
4. Minor issues (suggestions)
5. Security findings
6. Coverage gaps
7. Summary recommendation

Be direct. Flag every issue. No false positives, no missed negatives."""

_DEPLOY_SYSTEM = """You are the Deploy Agent for ProjectZeroFactory.
Your role: prepare release artifacts for a completed feature.

Output a Markdown document with:
1. Changelog entry (Keep a Changelog format)
2. Release tag recommendation (semver)
3. Deployment checklist (pre-deploy, deploy, post-deploy steps)
4. Rollback plan
5. Stakeholder notification draft

Be precise about versions and steps."""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SKILL_REGISTRY: dict[str, SkillDefinition] = {
    "spec": SkillDefinition(
        skill_id="spec",
        name="Spec Agent",
        description="Parse JIRA feature ticket → complete specification document with user stories and acceptance criteria.",
        system_prompt=_SPEC_SYSTEM,
        quality_gate=_gate_spec,
    ),
    "arch": SkillDefinition(
        skill_id="arch",
        name="Arch Agent",
        description="Design system architecture → ADR with component diagram, data models, API contracts.",
        system_prompt=_ARCH_SYSTEM,
        quality_gate=_gate_arch,
    ),
    "implement": SkillDefinition(
        skill_id="implement",
        name="Impl Agent",
        description="Implement feature via strict TDD → test file, implementation file, commit message.",
        system_prompt=_IMPL_SYSTEM,
        quality_gate=_gate_implement,
    ),
    "review": SkillDefinition(
        skill_id="review",
        name="Review Agent",
        description="Perform static analysis and code review → verdict (APPROVED/CHANGES_REQUIRED/REJECTED) with findings.",
        system_prompt=_REVIEW_SYSTEM,
        quality_gate=_gate_review,
    ),
    "deploy": SkillDefinition(
        skill_id="deploy",
        name="Deploy Agent",
        description="Prepare release artifacts → changelog entry, semver tag, deployment checklist, rollback plan.",
        system_prompt=_DEPLOY_SYSTEM,
        quality_gate=_gate_deploy,
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_skill(skill_id: str) -> SkillDefinition:
    """Return SkillDefinition for skill_id. Raises KeyError if not found."""
    if skill_id not in SKILL_REGISTRY:
        raise KeyError(f"Unknown skill: '{skill_id}'. Available: {list(SKILL_REGISTRY)}")
    return SKILL_REGISTRY[skill_id]


def list_skills() -> list[dict]:
    """Return [{skill_id, name, description}] for all registered skills."""
    return [
        {"skill_id": s.skill_id, "name": s.name, "description": s.description}
        for s in SKILL_REGISTRY.values()
    ]
