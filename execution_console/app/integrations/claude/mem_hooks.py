"""
claude-mem hook integration contract — PRJ0-72

Defines endpoints, constants, and utilities for the claude-mem lifecycle
hook integration. Used by shell hooks and test utilities.

Worker default port: 37777 (override via CLAUDE_MEM_PORT env var).
"""
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Endpoint constants
# ---------------------------------------------------------------------------

WORKER_HEALTH = "/health"
WORKER_OBSERVE = "/observe"
WORKER_SYNC = "/sync"
WORKER_COMPRESS = "/compress"
WORKER_FINALIZE = "/finalize"


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def get_worker_url(port: int = 37777) -> str:
    """Return base URL for the claude-mem worker."""
    return f"http://localhost:{port}"


def is_worker_running(port: int = 37777) -> bool:
    """
    Check if claude-mem worker is running by hitting /health.

    Returns True if worker responds, False on any error.
    Never raises — safe to call from hooks.
    """
    url = f"{get_worker_url(port)}{WORKER_HEALTH}"
    try:
        with urllib.request.urlopen(url, timeout=1) as resp:  # noqa: S310
            return resp.status == 200
    except Exception:
        return False
