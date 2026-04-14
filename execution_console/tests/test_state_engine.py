"""Unit tests — state engine build_snapshot — PRJ0-56."""
import pytest
from unittest.mock import patch
from execution_console.app.models.events import ExecStatus
from execution_console.app.services.state_engine import build_snapshot, _rollup_status


MOCK_TICKETS = [
    {
        "id": "evt-1", "event_type": "ticket_status",
        "feature_id": "feature:agents", "epic_key": "EPIC-AGENT",
        "ticket_id": "PRJ0-49", "workflow_run_id": "wf-001",
        "workflow_name": "FeatureDevelopmentWorkflow",
        "step": "impl_activity", "agent": "impl-agent",
        "status": "RUNNING", "pct": 67.0,
        "elapsed_ms": 45000, "retry_count": 0, "error": None,
        "jira_url": "https://jira.example.com/browse/PRJ0-49",
        "temporal_url": "http://localhost:8233/namespaces/default/workflows/wf-001",
        "log_url": None, "trace_url": None, "ts": "2026-04-14T10:00:00",
    },
    {
        "id": "evt-2", "event_type": "ticket_status",
        "feature_id": "feature:agents", "epic_key": "EPIC-AGENT",
        "ticket_id": "PRJ0-50", "workflow_run_id": "wf-002",
        "workflow_name": "FeatureDevelopmentWorkflow",
        "step": "spec_activity", "agent": "spec-agent",
        "status": "SUCCESS", "pct": 100.0,
        "elapsed_ms": 30000, "retry_count": 0, "error": None,
        "jira_url": None, "temporal_url": None, "log_url": None, "trace_url": None,
        "ts": "2026-04-14T09:00:00",
    },
]

MOCK_WORKFLOWS = [
    {
        "id": "evt-1", "workflow_run_id": "wf-001",
        "workflow_name": "FeatureDevelopmentWorkflow", "ticket_id": "PRJ0-49",
        "status": "RUNNING", "pct": 67.0,
        "temporal_url": "http://localhost:8233/namespaces/default/workflows/wf-001",
        "ts": "2026-04-14T10:00:00",
    },
]


@patch("execution_console.app.services.event_store.latest_per_ticket", return_value=MOCK_TICKETS)
@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=MOCK_WORKFLOWS)
def test_build_snapshot_running_ticket(mock_wf, mock_tickets):
    snapshot = build_snapshot()
    assert snapshot.overall_pct >= 0
    assert snapshot.running_count >= 1

    # Find the Agent System feature
    agent_feature = next((f for f in snapshot.features if f.name == "Agent System"), None)
    assert agent_feature is not None

    # Find EPIC-AGENT
    epic = next((e for e in agent_feature.epics if e.key == "EPIC-AGENT"), None)
    assert epic is not None

    # Find PRJ0-49 (running)
    t49 = next((t for t in epic.tickets if t.key == "PRJ0-49"), None)
    assert t49 is not None
    assert t49.status == ExecStatus.RUNNING
    assert t49.pct == 67.0


@patch("execution_console.app.services.event_store.latest_per_ticket", return_value=[])
@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
def test_build_snapshot_empty(mock_wf, mock_tickets):
    snapshot = build_snapshot()
    assert snapshot.overall_pct == 0.0
    assert snapshot.running_count == 0
    assert snapshot.failed_count == 0


@patch("execution_console.app.services.event_store.latest_per_ticket", return_value=MOCK_TICKETS)
@patch("execution_console.app.services.event_store.latest_per_workflow", return_value=[])
def test_build_snapshot_counts(mock_wf, mock_tickets):
    snapshot = build_snapshot()
    all_tickets = [t for f in snapshot.features for e in f.epics for t in e.tickets]
    running = [t for t in all_tickets if t.status == ExecStatus.RUNNING]
    success = [t for t in all_tickets if t.status == ExecStatus.SUCCESS]
    assert len(running) == 1
    assert len(success) >= 1
