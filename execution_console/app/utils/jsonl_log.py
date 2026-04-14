"""JSONL event logger — local traceability without a full DB — PRJ0-56."""
from __future__ import annotations
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_LOG_PATH: Optional[str] = None


def _log_path() -> Path:
    global _LOG_PATH
    path = Path(_LOG_PATH or os.getenv("CONSOLE_LOG_PATH", str(Path.home() / ".projectzero" / "events.jsonl")))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def configure(log_path: str) -> None:
    global _LOG_PATH
    _LOG_PATH = log_path


def append(event: dict) -> None:
    """Append event dict as a single JSON line to the log file."""
    try:
        record = {**event, "_logged_at": datetime.utcnow().isoformat()}
        with open(_log_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as exc:
        logger.debug(f"JSONL log write failed: {exc}")


def tail(n: int = 50) -> list[dict]:
    """Return last N events from the log file."""
    path = _log_path()
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(line) for line in lines[-n:] if line.strip()]
    except Exception as exc:
        logger.debug(f"JSONL log read failed: {exc}")
        return []


def clear() -> None:
    path = _log_path()
    if path.exists():
        path.unlink()
