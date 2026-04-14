"""MCRA workflow unit tests using Temporal test environment — PRJ0-67."""
import pytest

from app.temporal_integration.mcra_workflow import MCRAWorkflow, MCRAInput, MCRAResult


def test_mcra_input_dataclass():
    """MCRAInput can be constructed with required fields."""
    inp = MCRAInput(
        workflow_run_id="wf-test-001",
        product_id="prod-001",
        product_name="Test Product",
        repo_path="/tmp/test",
        jira_project_key="PRJ0",
        feature_id="PRJ0-49",
        impl_artifact_path="/tmp/test/.claude/impl/PRJ0-49-impl.md",
    )
    assert inp.feature_id == "PRJ0-49"
    assert inp.workflow_run_id == "wf-test-001"


def test_mcra_result_dataclass():
    """MCRAResult stores verdict and approval state."""
    result = MCRAResult(
        approved=True,
        stage="approver",
        verdict="approved",
        reviewer_summary="Looks good",
        approver_comment="LGTM",
    )
    assert result.approved is True
    assert result.verdict == "approved"


def test_mcra_result_defaults():
    """MCRAResult optional fields default to empty string."""
    result = MCRAResult(approved=False, stage="checker", verdict="gate_failed")
    assert result.reviewer_summary == ""
    assert result.approver_comment == ""


def test_mcra_workflow_signal_handler():
    """MCRAWorkflow signal handler sets approval state correctly."""
    wf = MCRAWorkflow()
    assert wf._approval_received is False

    wf.handle_approval(approved=True, comment="Approved by PM")
    assert wf._approval_received is True
    assert wf._approval_approved is True
    assert wf._approval_comment == "Approved by PM"


def test_mcra_workflow_reject_signal():
    """MCRAWorkflow handles rejection signal."""
    wf = MCRAWorkflow()
    wf.handle_approval(approved=False, comment="Needs rework")
    assert wf._approval_received is True
    assert wf._approval_approved is False
    assert wf._approval_comment == "Needs rework"


def test_mcra_workflow_initial_state():
    """MCRAWorkflow initializes with correct defaults."""
    wf = MCRAWorkflow()
    assert wf._approval_received is False
    assert wf._approval_approved is False
    assert wf._approval_comment == ""


def test_mcra_workflow_approve_no_comment():
    """MCRAWorkflow signal works with empty comment (default)."""
    wf = MCRAWorkflow()
    wf.handle_approval(approved=True)
    assert wf._approval_received is True
    assert wf._approval_comment == ""


def test_mcra_input_all_fields():
    """MCRAInput stores all fields correctly."""
    inp = MCRAInput(
        workflow_run_id="wf-999",
        product_id="prod-xyz",
        product_name="My Product",
        repo_path="/repo/path",
        jira_project_key="DEMO",
        feature_id="DEMO-5",
        impl_artifact_path="/repo/path/.claude/impl/DEMO-5-impl.md",
    )
    assert inp.product_name == "My Product"
    assert inp.jira_project_key == "DEMO"
    assert inp.impl_artifact_path == "/repo/path/.claude/impl/DEMO-5-impl.md"
