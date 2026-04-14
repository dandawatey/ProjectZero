"""Ticket router workflow tests — PRJ0-67."""
import inspect
import pytest


def test_ticket_router_workflow_importable():
    """TicketRouterWorkflow can be imported without error."""
    from app.temporal_integration.ticket_router_workflow import TicketRouterWorkflow, TicketRouterInput
    assert TicketRouterWorkflow is not None


def test_ticket_router_input_importable():
    """TicketRouterInput dataclass importable and constructable."""
    from app.temporal_integration.ticket_router_workflow import TicketRouterInput
    inp = TicketRouterInput(
        workflow_run_id="wf-001",
        product_id="prod-001",
        product_name="Test",
        repo_path="/tmp/test",
        jira_project_key="PRJ0",
        ticket_id="PRJ0-10",
        ticket_type="Story",
        title="Test ticket",
        description="Test description",
    )
    assert inp.ticket_id == "PRJ0-10"
    assert inp.child_ticket_ids == []


def test_mcra_workflow_importable():
    """MCRAWorkflow can be imported without error."""
    from app.temporal_integration.mcra_workflow import MCRAWorkflow, MCRAInput, MCRAResult
    assert MCRAWorkflow is not None


def test_mcra_activities_importable():
    """MCRA activities can be imported without error."""
    from app.temporal_integration.mcra_activities import (
        mcra_checker_activity,
        mcra_reviewer_activity,
        mcra_notify_activity,
    )
    assert mcra_checker_activity is not None
    assert mcra_reviewer_activity is not None
    assert mcra_notify_activity is not None


def test_worker_workflow_list():
    """Worker registers expected workflows."""
    import app.temporal_integration.worker as worker_module
    source = inspect.getsource(worker_module)
    assert "MCRAWorkflow" in source
    assert "FeatureDevelopmentWorkflow" in source


def test_worker_registers_mcra_activities():
    """Worker registers all MCRA activities."""
    import app.temporal_integration.worker as worker_module
    source = inspect.getsource(worker_module)
    assert "mcra_checker_activity" in source
    assert "mcra_reviewer_activity" in source
    assert "mcra_notify_activity" in source


def test_worker_registers_ticket_router():
    """Worker registers TicketRouterWorkflow."""
    import app.temporal_integration.worker as worker_module
    source = inspect.getsource(worker_module)
    assert "TicketRouterWorkflow" in source


def test_quality_gate_runner_importable():
    """QualityGateRunner imports cleanly."""
    from app.services.quality_gate import run_quality_gates, CheckResult, GateResult
    assert run_quality_gates is not None
    assert CheckResult is not None
    assert GateResult is not None


def test_quality_gate_on_nonexistent_path():
    """run_quality_gates handles missing repo path gracefully."""
    from app.services.quality_gate import run_quality_gates
    result = run_quality_gates("/nonexistent/path/xyz")
    assert result is not None
    assert hasattr(result, "passed")
    assert hasattr(result, "gates")
    assert isinstance(result.gates, list)
    assert len(result.gates) == 3  # coverage, lint, types


def test_check_result_structure():
    """CheckResult has expected fields."""
    from app.services.quality_gate import CheckResult, GateResult
    gr = GateResult(name="coverage", passed=True, score="85.0%")
    cr = CheckResult(passed=True, gates=[gr], coverage_pct=85.0, lint_errors=0, type_errors=0)
    assert cr.passed is True
    assert cr.coverage_pct == 85.0
    assert len(cr.gates) == 1


def test_gate_result_structure():
    """GateResult has expected fields."""
    from app.services.quality_gate import GateResult
    gr = GateResult(name="lint", passed=False, score="3 errors", detail="3 ruff violations")
    assert gr.name == "lint"
    assert gr.passed is False
    assert gr.detail == "3 ruff violations"
