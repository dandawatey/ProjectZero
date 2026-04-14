#!/usr/bin/env python3
"""Start FastAPI backend + Rich console sidecar — PRJ0-56."""
import subprocess, sys, time, threading
from pathlib import Path

def start_api():
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "execution_console.app.main:app",
        "--host", "0.0.0.0", "--port", "8001",
        "--log-level", "error",
    ])

def start_console():
    time.sleep(2)  # wait for API
    import httpx
    from execution_console.app.services.state_engine import build_snapshot
    from execution_console.app.renderers.rich_console import run_live_console

    def fetch():
        try:
            r = httpx.get("http://localhost:8001/api/v1/snapshot", timeout=5)
            from execution_console.app.models.events import StatusSnapshot
            return StatusSnapshot(**r.json())
        except Exception:
            return build_snapshot()  # fallback to local

    run_live_console(fetch_snapshot=fetch, refresh_seconds=2.0)

if __name__ == "__main__":
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    start_console()
