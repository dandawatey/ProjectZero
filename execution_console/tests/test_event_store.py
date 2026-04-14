"""Event store tests — PRJ0-70."""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from unittest.mock import patch


@pytest.fixture()
def store(tmp_path):
    """Provide a clean event_store backed by tmp SQLite DB."""
    db_path = str(tmp_path / "test_console.db")

    # Patch DB_PATH and _conn at module level
    import execution_console.app.services.event_store as es

    def _tmp_conn():
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(db_path)
        c.row_factory = sqlite3.Row
        return c

    with patch.object(es, "_conn", _tmp_conn):
        es.init_db()
        yield es


def test_store_and_retrieve_event(store):
    from execution_console.app.models.events import ExecutionEvent, ExecStatus
    event = ExecutionEvent(
        event_type="ticket_status",
        ticket_id="PRJ0-49",
        epic_key="EPIC-AGENT",
        feature_id="feature:agents",
        status=ExecStatus.RUNNING,
        pct=45.0,
        agent="impl-agent",
    )
    store.store_event(event)
    tickets = store.latest_per_ticket()
    assert len(tickets) >= 1
    pj49 = [t for t in tickets if t["ticket_id"] == "PRJ0-49"]
    assert len(pj49) == 1
    assert pj49[0]["status"] == "RUNNING"
    assert pj49[0]["pct"] == 45.0


def test_latest_per_ticket_returns_newest(store):
    from execution_console.app.models.events import ExecutionEvent, ExecStatus
    import time
    e1 = ExecutionEvent(event_type="step", ticket_id="PRJ0-50", status=ExecStatus.RUNNING, pct=20.0)
    store.store_event(e1)
    time.sleep(0.01)
    e2 = ExecutionEvent(event_type="step", ticket_id="PRJ0-50", status=ExecStatus.SUCCESS, pct=100.0)
    store.store_event(e2)
    tickets = store.latest_per_ticket()
    pj50 = [t for t in tickets if t["ticket_id"] == "PRJ0-50"]
    assert len(pj50) == 1
    assert pj50[0]["pct"] == 100.0


def test_failed_events_filter(store):
    from execution_console.app.models.events import ExecutionEvent, ExecStatus
    good = ExecutionEvent(event_type="step", ticket_id="PRJ0-51", status=ExecStatus.SUCCESS, pct=100.0)
    bad = ExecutionEvent(event_type="step", ticket_id="PRJ0-52", status=ExecStatus.FAILED, error="timeout")
    store.store_event(good)
    store.store_event(bad)
    failed = store.failed_events()
    failed_keys = [f["ticket_id"] for f in failed]
    assert "PRJ0-52" in failed_keys
    assert "PRJ0-51" not in failed_keys


def test_clear_all(store):
    from execution_console.app.models.events import ExecutionEvent, ExecStatus
    store.store_event(ExecutionEvent(event_type="step", ticket_id="PRJ0-53", status=ExecStatus.RUNNING))
    store.clear_all()
    assert store.latest_per_ticket() == []


def test_store_event_preserves_error_field(store):
    from execution_console.app.models.events import ExecutionEvent, ExecStatus
    event = ExecutionEvent(
        event_type="step",
        ticket_id="PRJ0-54",
        status=ExecStatus.FAILED,
        error="connection timeout after 30s",
    )
    store.store_event(event)
    failed = store.failed_events()
    pj54 = [f for f in failed if f["ticket_id"] == "PRJ0-54"]
    assert len(pj54) == 1
    assert pj54[0]["error"] == "connection timeout after 30s"


def test_latest_per_workflow(store):
    from execution_console.app.models.events import ExecutionEvent, ExecStatus
    event = ExecutionEvent(
        event_type="workflow_start",
        workflow_run_id="wf-abc",
        workflow_name="FeatureDevelopmentWorkflow",
        status=ExecStatus.RUNNING,
        pct=0.0,
    )
    store.store_event(event)
    workflows = store.latest_per_workflow()
    assert len(workflows) >= 1


def test_multiple_tickets_in_store(store):
    from execution_console.app.models.events import ExecutionEvent, ExecStatus
    for i in range(5):
        store.store_event(ExecutionEvent(
            event_type="step",
            ticket_id=f"PRJ0-{100+i}",
            status=ExecStatus.QUEUED,
            pct=0.0,
        ))
    tickets = store.latest_per_ticket()
    keys = [t["ticket_id"] for t in tickets]
    for i in range(5):
        assert f"PRJ0-{100+i}" in keys
