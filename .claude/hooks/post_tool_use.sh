#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Claude Code PostToolUse hook — emit execution event to Execution Console
# File: .claude/hooks/post_tool_use.sh
# PRJ0-56
#
# HOW IT WORKS:
#   Claude Code fires this script after every tool call.
#   If CLAUDE_CURRENT_TICKET is set, we POST a structured event to the
#   Execution Console backend so the terminal dashboard stays live.
#
# SETUP:
#   export CLAUDE_CURRENT_TICKET=PRJ0-49   # ticket you're working on
#   export CLAUDE_AGENT_NAME=impl-agent    # your agent role
#   Start Claude Code. Hook fires automatically on every tool use.
#
# EVENT FORMAT: see execution_console/app/integrations/claude/hook_events.py
# ──────────────────────────────────────────────────────────────────────────────

CONSOLE_URL="${EXECUTION_CONSOLE_URL:-http://localhost:8001}"
TICKET="${CLAUDE_CURRENT_TICKET:-}"
AGENT="${CLAUDE_AGENT_NAME:-claude}"

# No ticket set → silent exit (no noise when not actively on a ticket)
if [ -z "$TICKET" ]; then
    exit 0
fi

# Check if console is reachable (non-blocking health check)
curl -s -o /dev/null --connect-timeout 1 "${CONSOLE_URL}/api/v1/health" 2>/dev/null || exit 0

# Determine status from tool context (Claude Code may provide these via env)
TOOL="${CLAUDE_TOOL_NAME:-tool_use}"
STATUS="RUNNING"

# Map specific tools to status signals
case "$TOOL" in
    "Bash"|"Write"|"Edit"|"NotebookEdit") STATUS="RUNNING" ;;
esac

# Emit event (fire-and-forget, don't block Claude Code)
curl -s -X POST "${CONSOLE_URL}/api/v1/events" \
    --connect-timeout 2 \
    -H "Content-Type: application/json" \
    -d "{
        \"event_type\": \"tool_use\",
        \"ticket_id\": \"${TICKET}\",
        \"step\": \"${TOOL}\",
        \"agent\": \"${AGENT}\",
        \"status\": \"${STATUS}\",
        \"pct\": 50.0
    }" > /dev/null 2>&1 &

exit 0
