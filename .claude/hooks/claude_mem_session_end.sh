#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Claude Code SessionEnd hook — finalize claude-mem session
# File: .claude/hooks/claude_mem_session_end.sh
# PRJ0-72
#
# Env vars:
#   CLAUDE_MEM_PORT    worker port (default 37777)
#   CLAUDE_MEM_ENABLED if "false", skip entirely (default true)
# ──────────────────────────────────────────────────────────────────────────────

PORT="${CLAUDE_MEM_PORT:-37777}"
BASE="http://localhost:${PORT}"

# Respect kill-switch
if [ "${CLAUDE_MEM_ENABLED:-true}" = "false" ]; then
    exit 0
fi

# Fire-and-forget finalize — ignore if worker not running
curl -s -X POST "${BASE}/finalize" --connect-timeout 2 -o /dev/null 2>/dev/null &

exit 0
