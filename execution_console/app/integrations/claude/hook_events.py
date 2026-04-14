"""
Claude Code Hook Integration — event contract + emitter — PRJ0-56.

Claude Code runs hooks defined in .claude/settings.json:
  - PreToolUse:  fires before a tool call
  - PostToolUse: fires after a tool call completes

The hook script (.claude/hooks/post_tool_use.sh) reads env vars set by
the developer (CLAUDE_CURRENT_TICKET, CLAUDE_AGENT_NAME) and POSTs a
structured ExecutionEvent to the console backend.

NORMAL MODE:
  Hook reads env vars → builds JSON payload → POST /api/v1/events.
  Console backend stores event → state engine rolls up → renderer shows update.

Event type reference:
  tool_use        — a Claude Code tool was invoked (file edit, bash, glob, etc.)
  workflow_start  — a Temporal workflow started for this ticket
  workflow_end    — a Temporal workflow completed/failed
  step_start      — a workflow activity/step started
  step_end        — a workflow activity/step completed
  ticket_status   — explicit ticket status update (manual or from JIRA webhook)
  agent_start     — an agent sub-task started
  agent_end       — an agent sub-task completed
"""
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from ...__init__ import __all__  # noqa: F401 — silence unused import linter


# ── Hook event schema (what .claude/hooks/post_tool_use.sh emits) ──────────

HOOK_EVENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "HookEvent",
    "description": "Event emitted by Claude Code hooks to the Execution Console",
    "type": "object",
    "required": ["event_type"],
    "properties": {
        "event_type": {
            "type": "string",
            "enum": [
                "tool_use", "workflow_start", "workflow_end",
                "step_start", "step_end", "ticket_status",
                "agent_start", "agent_end",
            ],
        },
        "ticket_id":        {"type": "string", "example": "PRJ0-49"},
        "epic_key":         {"type": "string", "example": "EPIC-AGENT"},
        "feature_id":       {"type": "string", "example": "feature:agents"},
        "workflow_run_id":  {"type": "string", "example": "wf-prj0-49-001"},
        "workflow_name":    {"type": "string", "example": "FeatureDevelopmentWorkflow"},
        "step":             {"type": "string", "example": "impl_activity"},
        "agent":            {"type": "string", "example": "impl-agent"},
        "status": {
            "type": "string",
            "enum": ["QUEUED", "RUNNING", "SUCCESS", "FAILED", "BLOCKED", "RETRYING", "CANCELLED"],
        },
        "pct":              {"type": "number", "minimum": 0, "maximum": 100},
        "elapsed_ms":       {"type": "integer"},
        "retry_count":      {"type": "integer", "default": 0},
        "error":            {"type": "string"},
        "jira_url":         {"type": "string", "format": "uri"},
        "temporal_url":     {"type": "string", "format": "uri"},
        "log_url":          {"type": "string"},
        "trace_url":        {"type": "string"},
    },
}


# ── Programmatic emitter (Python SDK path) ─────────────────────────────────

class HookEventEmitter:
    """
    Emit execution events from Python code (Temporal activities, agent workers).

    Usage:
        emitter = HookEventEmitter("http://localhost:8001")
        emitter.emit(ticket_id="PRJ0-49", event_type="step_start",
                     step="impl_activity", agent="impl-agent", pct=10.0)
    """

    def __init__(self, console_url: str = "http://localhost:8001"):
        self._url = console_url.rstrip("/")

    def emit(
        self,
        event_type: str,
        ticket_id: Optional[str] = None,
        epic_key: Optional[str] = None,
        feature_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
        step: Optional[str] = None,
        agent: Optional[str] = None,
        status: str = "RUNNING",
        pct: float = 0.0,
        elapsed_ms: Optional[int] = None,
        retry_count: int = 0,
        error: Optional[str] = None,
        jira_url: Optional[str] = None,
        temporal_url: Optional[str] = None,
        log_url: Optional[str] = None,
        trace_url: Optional[str] = None,
    ) -> bool:
        """POST event to console backend. Returns True on success, False on error."""
        try:
            import httpx
            payload = {
                k: v for k, v in {
                    "event_type": event_type,
                    "ticket_id": ticket_id,
                    "epic_key": epic_key,
                    "feature_id": feature_id,
                    "workflow_run_id": workflow_run_id,
                    "workflow_name": workflow_name,
                    "step": step,
                    "agent": agent,
                    "status": status,
                    "pct": pct,
                    "elapsed_ms": elapsed_ms,
                    "retry_count": retry_count,
                    "error": error,
                    "jira_url": jira_url,
                    "temporal_url": temporal_url,
                    "log_url": log_url,
                    "trace_url": trace_url,
                }.items() if v is not None
            }
            r = httpx.post(f"{self._url}/api/v1/events", json=payload, timeout=3)
            return r.status_code == 201
        except Exception:
            return False


# ── Shell hook contract (for documentation) ────────────────────────────────

SHELL_HOOK_CONTRACT = """
# .claude/hooks/post_tool_use.sh — Claude Code PostToolUse hook
#
# Env vars set by developer in their shell session:
#   CLAUDE_CURRENT_TICKET   — e.g. PRJ0-49  (which ticket is being worked on)
#   CLAUDE_AGENT_NAME       — e.g. impl-agent (which agent role you're running as)
#   EXECUTION_CONSOLE_URL   — defaults to http://localhost:8001
#
# Env vars provided by Claude Code hook runtime (PostToolUse):
#   CLAUDE_TOOL_NAME        — name of tool that was used (Write, Edit, Bash, etc.)
#   CLAUDE_TOOL_STATUS      — exit status of the tool
#
# The hook fires after EVERY tool use. If CLAUDE_CURRENT_TICKET is unset,
# hook exits immediately (no noise when not actively working a ticket).
"""
