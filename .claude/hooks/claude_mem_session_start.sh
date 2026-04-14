#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Claude Code SessionStart hook — start claude-mem worker if not running
# File: .claude/hooks/claude_mem_session_start.sh
# PRJ0-72
#
# Env vars:
#   CLAUDE_MEM_PORT    worker port (default 37777)
#   CLAUDE_MEM_ENABLED if "false", skip entirely (default true)
# ──────────────────────────────────────────────────────────────────────────────

PORT="${CLAUDE_MEM_PORT:-37777}"

# Respect kill-switch
if [ "${CLAUDE_MEM_ENABLED:-true}" = "false" ]; then
    exit 0
fi

# Health check — if worker already up, done
if curl -s -o /dev/null --connect-timeout 1 "http://localhost:${PORT}/health" 2>/dev/null; then
    exit 0
fi

# Worker not running — try to start in background, silently
if command -v npx >/dev/null 2>&1; then
    npx claude-mem start 2>/dev/null &
fi

# Always exit 0 — never block Claude Code
exit 0
