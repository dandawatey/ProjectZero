#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Claude Code Stop/SessionEnd hook — sync claude-mem → Brain (Postgres)
# File: .claude/hooks/claude_mem_brain_sync.sh
# PRJ0-71
#
# Reads high-relevance observations + session summaries from claude-mem SQLite
# and promotes them to ProjectZero Brain API.
# Fire-and-forget — never blocks Claude Code.
# ──────────────────────────────────────────────────────────────────────────────

# Respect kill-switch
if [ "${CLAUDE_MEM_ENABLED:-true}" = "false" ]; then
    exit 0
fi

# Find repo root (where platform/backend lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND="$REPO_ROOT/platform/backend"

# Run sync in background — don't block session end
(
    cd "$BACKEND" || exit 0
    if [ -f ".env" ]; then
        set -a; source .env 2>/dev/null; set +a
    fi
    # Try uv first, then python3
    if command -v uv >/dev/null 2>&1; then
        uv run python -m app.services.claude_mem_sync 2>/dev/null
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m app.services.claude_mem_sync 2>/dev/null
    fi
) &

exit 0
