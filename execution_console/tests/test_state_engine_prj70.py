"""State engine rollup tests — PRJ0-70."""
import pytest
from unittest.mock import patch

from execution_console.app.models.events import ExecStatus


def _make_ticket_row(ticket_id, status_str, pct, feature_id="feature:agents", epic_key="EPIC-AGENT"):
    return {
        "id": f"evt-{ticket_id}",
        "event_type": "ticket_status",
        "ticket_id": ticket_id,
        "feature_id": feature_id,
        "epic_key": epic_key,
        "workflow_run_id": None,
        "workflow_name": None,
        "step": None,
        "agent": None,
        "status": status_str,
        "pct": pct,
        "elapsed_ms": None,
        "retry_count": 0,
        "error": None,
        "jira_url": None,
        "temporal_url": None,
        "log_url": None,
        "trace_url": None,
        "ts": "2026-04-14T10:00:00",
    }


@patch("execution_console.app.services.event_store.latest_per_ticket", return_value=[])
@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
def test_snapshot_empty_store(mock_wf, mock_tickets):
    from execution_console.app.services.state_engine import build_snapshot
    snap = build_snapshot()
    assert snap.overall_pct == 0.0
    assert snap.running_count == 0
    assert snap.failed_count == 0
    assert len(snap.features) == 6


@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
@patch("execution_console.app.services.event_store.latest_per_ticket")
def test_running_ticket_propagates(mock_tickets, mock_wf):
    mock_tickets.return_value = [_make_ticket_row("PRJ0-49", "RUNNING", 50.0)]
    from execution_console.app.services.state_engine import build_snapshot
    snap = build_snapshot()
    assert snap.running_count >= 1
    agent_feature = next((f for f in snap.features if f.name == "Agent System"), None)
    assert agent_feature is not None
    assert agent_feature.status == ExecStatus.RUNNING


@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
@patch("execution_console.app.services.event_store.latest_per_ticket")
def test_failed_ticket_propagates(mock_tickets, mock_wf):
    mock_tickets.return_value = [_make_ticket_row("PRJ0-49", "FAILED", 0.0)]
    from execution_console.app.services.state_engine import build_snapshot
    snap = build_snapshot()
    assert snap.failed_count >= 1


@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
@patch("execution_console.app.services.event_store.latest_per_ticket")
def test_all_success_100_pct(mock_tickets, mock_wf):
    rows = [
        _make_ticket_row(k, "SUCCESS", 100.0)
        for k in ["PRJ0-10", "PRJ0-44", "PRJ0-49", "PRJ0-50", "PRJ0-51", "PRJ0-52", "PRJ0-53"]
    ]
    mock_tickets.return_value = rows
    from execution_console.app.services.state_engine import build_snapshot
    snap = build_snapshot()
    agent_feature = next((f for f in snap.features if f.name == "Agent System"), None)
    assert agent_feature is not None
    assert agent_feature.pct == 100.0
    assert agent_feature.status == ExecStatus.SUCCESS


@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
@patch("execution_console.app.services.event_store.latest_per_ticket")
def test_overall_pct_increases_with_success(mock_tickets, mock_wf):
    from execution_console.app.services.state_engine import build_snapshot
    mock_tickets.return_value = []
    snap_before = build_snapshot()

    mock_tickets.return_value = [_make_ticket_row("PRJ0-49", "SUCCESS", 100.0)]
    snap_after = build_snapshot()

    assert snap_after.overall_pct >= snap_before.overall_pct


@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
@patch("execution_console.app.services.event_store.latest_per_ticket")
def test_snapshot_has_all_six_features(mock_tickets, mock_wf):
    mock_tickets.return_value = []
    from execution_console.app.services.state_engine import build_snapshot, FEATURE_MAP
    snap = build_snapshot()
    feature_names = {f.name for f in snap.features}
    assert feature_names == set(FEATURE_MAP.keys())


@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
@patch("execution_console.app.services.event_store.latest_per_ticket")
def test_queued_default_status(mock_tickets, mock_wf):
    """Tickets with no events default to QUEUED."""
    mock_tickets.return_value = []
    from execution_console.app.services.state_engine import build_snapshot
    snap = build_snapshot()
    all_tickets = [t for f in snap.features for e in f.epics for t in e.tickets]
    queued = [t for t in all_tickets if t.status == ExecStatus.QUEUED]
    assert len(queued) == len(all_tickets)
