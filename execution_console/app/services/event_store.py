"""SQLite-backed event store — PRJ0-56."""
from __future__ import annotations
import json, logging, os, sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.events import ExecutionEvent, ExecStatus

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("CONSOLE_DB_PATH", str(Path.home() / ".projectzero" / "console.db"))


def _conn() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                event_type TEXT,
                feature_id TEXT,
                epic_key TEXT,
                ticket_id TEXT,
                workflow_run_id TEXT,
                workflow_name TEXT,
                step TEXT,
                agent TEXT,
                status TEXT,
                pct REAL,
                elapsed_ms INTEGER,
                retry_count INTEGER DEFAULT 0,
                error TEXT,
                jira_url TEXT,
                temporal_url TEXT,
                log_url TEXT,
                trace_url TEXT,
                ts TEXT
            )
        """)
        c.commit()


def store_event(event: ExecutionEvent) -> None:
    with _conn() as c:
        c.execute("""
            INSERT OR REPLACE INTO events
            (id, event_type, feature_id, epic_key, ticket_id, workflow_run_id,
             workflow_name, step, agent, status, pct, elapsed_ms, retry_count,
             error, jira_url, temporal_url, log_url, trace_url, ts)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            event.id, event.event_type, event.feature_id, event.epic_key,
            event.ticket_id, event.workflow_run_id, event.workflow_name,
            event.step, event.agent, event.status.value, event.pct,
            event.elapsed_ms, event.retry_count, event.error,
            event.jira_url, event.temporal_url, event.log_url, event.trace_url,
            event.ts.isoformat(),
        ))
        c.commit()


def latest_per_ticket() -> list[dict]:
    """Return latest event per ticket_id."""
    with _conn() as c:
        rows = c.execute("""
            SELECT * FROM events
            WHERE ticket_id IS NOT NULL
            GROUP BY ticket_id
            HAVING ts = MAX(ts)
            ORDER BY ts DESC
        """).fetchall()
    return [dict(r) for r in rows]


def latest_per_workflow() -> list[dict]:
    with _conn() as c:
        rows = c.execute("""
            SELECT * FROM events
            WHERE workflow_run_id IS NOT NULL
            GROUP BY workflow_run_id
            HAVING ts = MAX(ts)
            ORDER BY ts DESC LIMIT 50
        """).fetchall()
    return [dict(r) for r in rows]


def failed_events() -> list[dict]:
    with _conn() as c:
        rows = c.execute("""
            SELECT * FROM events WHERE status = 'FAILED'
            ORDER BY ts DESC LIMIT 20
        """).fetchall()
    return [dict(r) for r in rows]


def clear_all() -> None:
    with _conn() as c:
        c.execute("DELETE FROM events")
        c.commit()
