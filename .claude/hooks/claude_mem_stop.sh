#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Claude Code Stop hook — trigger Brain sync + memory compression
# File: .claude/hooks/claude_mem_stop.sh
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

# Silently exit if worker not reachable
if ! curl -s -o /dev/null --connect-timeout 1 "${BASE}/health" 2>/dev/null; then
    exit 0
fi

# Fire-and-forget: sync to Brain + compress memory
(curl -s -X POST "${BASE}/sync"     --connect-timeout 2 -o /dev/null 2>/dev/null &&
 curl -s -X POST "${BASE}/compress" --connect-timeout 2 -o /dev/null 2>/dev/null) &

exit 0
