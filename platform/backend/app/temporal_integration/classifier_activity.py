"""Ticket Classifier Activity.

Reads a JIRA ticket (title + description + type) and outputs:
  - workflow_type: story | bug | task | epic
  - risk_level:    low | medium | high | critical
  - requires_spec: bool
  - requires_arch: bool
  - auto_approve:  bool
  - summary:       ≤200 char human-readable routing decision

Routes to:
  epic  → EpicOrchestratorWorkflow
  story → FeatureDevelopmentWorkflow (Spec→Arch→Impl→Review→Deploy)
  bug   → BugFixWorkflow             (Diagnose→Fix→Verify)
  task  → TaskWorkflow               (Impl→Review, auto-approve)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass

from temporalio import activity

logger = logging.getLogger(__name__)


@dataclass
class TicketInput:
    ticket_id: str            # e.g. PRJ0-47
    title: str
    description: str
    ticket_type: str          # Epic | Story | Bug | Task | Sub-task
    product_id: str
    product_name: str
    repo_path: str
    jira_project_key: str


@dataclass
class ClassifierOutput:
    ticket_id: str
    workflow_type: str        # epic | story | bug | task
    risk_level: str           # low | medium | high | critical
    requires_spec: bool
    requires_arch: bool
    auto_approve: bool
    approval_count: int       # number of human approvals required
    routing_reason: str       # ≤200 chars


_CLASSIFIER_SYSTEM = """You are a ticket routing classifier for an AI-governed software factory.

Given a JIRA ticket, output a JSON object with exactly these fields:
{
  "workflow_type": "story" | "bug" | "task" | "epic",
  "risk_level": "low" | "medium" | "high" | "critical",
  "requires_spec": true | false,
  "requires_arch": true | false,
  "auto_approve": true | false,
  "approval_count": 0 | 1 | 2 | 3,
  "routing_reason": "≤200 char explanation"
}

Classification rules:
- Epic      → workflow_type=epic,  risk=high,   requires_spec=true,  requires_arch=true,  auto_approve=false, approvals=3
- Story     → workflow_type=story, risk=medium,  requires_spec=true,  requires_arch=true,  auto_approve=false, approvals=2
- Bug/crit  → workflow_type=bug,   risk=critical,requires_spec=false, requires_arch=false, auto_approve=false, approvals=2
- Bug/minor → workflow_type=bug,   risk=low,     requires_spec=false, requires_arch=false, auto_approve=true,  approvals=0
- Task/chore→ workflow_type=task,  risk=low,     requires_spec=false, requires_arch=false, auto_approve=true,  approvals=0
- Security  → always critical, approvals=3

Adjust risk upward for: auth, security, payment, data migration, schema change, performance.
Adjust risk downward for: docs, config, typo, dependency bump, logging.

Output ONLY the JSON object, no explanation."""


@activity.defn(name="classify_ticket_activity")
async def classify_ticket_activity(inp: TicketInput) -> ClassifierOutput:
    activity.heartbeat("Classifier: analysing ticket")

    from app.temporal_integration.activities import _call_claude

    user_prompt = f"""Ticket ID:   {inp.ticket_id}
Type:        {inp.ticket_type}
Title:       {inp.title}
Description: {inp.description[:1000]}

Classify this ticket and return routing JSON."""

    try:
        raw = _call_claude(_CLASSIFIER_SYSTEM, user_prompt)
        # Strip markdown fences if present
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        return ClassifierOutput(
            ticket_id=inp.ticket_id,
            workflow_type=data.get("workflow_type", "task"),
            risk_level=data.get("risk_level", "low"),
            requires_spec=data.get("requires_spec", False),
            requires_arch=data.get("requires_arch", False),
            auto_approve=data.get("auto_approve", True),
            approval_count=data.get("approval_count", 0),
            routing_reason=data.get("routing_reason", "classified as task"),
        )
    except Exception as exc:
        logger.warning("Classifier failed, defaulting to task: %s", exc)
        return ClassifierOutput(
            ticket_id=inp.ticket_id,
            workflow_type="task",
            risk_level="low",
            requires_spec=False,
            requires_arch=False,
            auto_approve=True,
            approval_count=0,
            routing_reason=f"Classifier error — defaulted to task: {exc}",
        )
