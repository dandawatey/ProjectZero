"""Unit tests — canonical models and status rollup — PRJ0-56."""
import pytest
from execution_console.app.models.events import (
    ExecStatus, ExecutionEvent, FeatureStatus, EpicStatus, TicketStatus,
    WorkflowStatus, StatusSnapshot,
)
from execution_console.app.services.state_engine import _rollup_status, _rollup_pct


class TestExecStatus:
    def test_all_values_exist(self):
        expected = {"QUEUED", "RUNNING", "SUCCESS", "FAILED", "BLOCKED", "RETRYING", "CANCELLED"}
        assert {s.value for s in ExecStatus} == expected

    def test_string_coercion(self):
        assert ExecStatus("RUNNING") == ExecStatus.RUNNING


class TestRollupStatus:
    def test_failed_wins(self):
        statuses = [ExecStatus.SUCCESS, ExecStatus.FAILED, ExecStatus.RUNNING]
        assert _rollup_status(statuses) == ExecStatus.FAILED

    def test_blocked_wins_over_running(self):
        statuses = [ExecStatus.RUNNING, ExecStatus.BLOCKED]
        assert _rollup_status(statuses) == ExecStatus.BLOCKED

    def test_running_wins_over_queued(self):
        statuses = [ExecStatus.QUEUED, ExecStatus.RUNNING]
        assert _rollup_status(statuses) == ExecStatus.RUNNING

    def test_all_success(self):
        statuses = [ExecStatus.SUCCESS, ExecStatus.SUCCESS]
        assert _rollup_status(statuses) == ExecStatus.SUCCESS

    def test_all_queued(self):
        statuses = [ExecStatus.QUEUED, ExecStatus.QUEUED]
        assert _rollup_status(statuses) == ExecStatus.QUEUED

    def test_empty_returns_queued(self):
        assert _rollup_status([]) == ExecStatus.QUEUED


class TestRollupPct:
    def test_average(self):
        assert _rollup_pct([0.0, 50.0, 100.0]) == pytest.approx(50.0, abs=0.1)

    def test_empty_returns_zero(self):
        assert _rollup_pct([]) == 0.0

    def test_all_done(self):
        assert _rollup_pct([100.0, 100.0]) == pytest.approx(100.0)


class TestExecutionEvent:
    def test_defaults(self):
        e = ExecutionEvent(event_type="tool_use")
        assert e.status == ExecStatus.QUEUED
        assert e.pct == 0.0
        assert e.retry_count == 0
        assert e.id is not None

    def test_full_event(self):
        e = ExecutionEvent(
            event_type="ticket_status",
            ticket_id="PRJ0-49",
            epic_key="EPIC-AGENT",
            feature_id="feature:agents",
            workflow_run_id="wf-001",
            workflow_name="FeatureDevelopmentWorkflow",
            step="impl_activity",
            agent="impl-agent",
            status=ExecStatus.RUNNING,
            pct=67.5,
        )
        assert e.ticket_id == "PRJ0-49"
        assert e.status == ExecStatus.RUNNING
        assert e.pct == 67.5


class TestStatusSnapshot:
    def test_build(self):
        ticket = TicketStatus(key="PRJ0-1", summary="test", status=ExecStatus.SUCCESS, pct=100.0)
        epic = EpicStatus(key="EPIC-1", summary="test epic", status=ExecStatus.SUCCESS, pct=100.0, tickets=[ticket])
        feature = FeatureStatus(name="Feature 1", status=ExecStatus.SUCCESS, pct=100.0, epics=[epic])
        snapshot = StatusSnapshot(
            features=[feature],
            overall_pct=100.0,
            running_count=0,
            failed_count=0,
            queued_count=0,
        )
        assert snapshot.overall_pct == 100.0
        assert len(snapshot.features) == 1
