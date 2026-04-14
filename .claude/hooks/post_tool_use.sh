#!/usr/bin/env bash
# Claude Code hook: emit execution event to Execution Console on tool use
# Place in .claude/hooks/post_tool_use.sh
# PRJ0-56

CONSOLE_URL="${EXECUTION_CONSOLE_URL:-http://localhost:8001}"
TOOL="${CLAUDE_TOOL_NAME:-unknown}"
STATUS="${CLAUDE_TOOL_STATUS:-RUNNING}"
TICKET="${CLAUDE_CURRENT_TICKET:-}"
AGENT="${CLAUDE_AGENT_NAME:-claude}"

if [ -z "$TICKET" ]; then exit 0; fi

curl -s -X POST "${CONSOLE_URL}/api/v1/events" \
  -H "Content-Type: application/json" \
  -d "{
    \"event_type\": \"tool_use\",
    \"ticket_id\": \"${TICKET}\",
    \"step\": \"${TOOL}\",
    \"agent\": \"${AGENT}\",
    \"status\": \"${STATUS}\",
    \"pct\": 50.0
  }" > /dev/null 2>&1 || true
