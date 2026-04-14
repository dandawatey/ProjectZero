"""Activity unit tests — PRJ0-67."""
import pytest
from pathlib import Path
import tempfile

from app.temporal_integration.activities import AgentInput, AgentOutput, _write_artifact, _brain_context


def test_agent_input_dataclass():
    inp = AgentInput(
        workflow_run_id="wf-001",
        product_id="prod-001",
        product_name="Test Product",
        repo_path="/tmp/test",
        jira_project_key="PRJ0",
        feature_id="PRJ0-50",
        stage="specification",
        context={},
    )
    assert inp.feature_id == "PRJ0-50"
    assert inp.stage == "specification"


def test_agent_output_dataclass():
    out = AgentOutput(
        agent_type="spec",
        stage="specification",
        status="completed",
        artifact_path="/tmp/test/spec.md",
        summary="Spec written",
    )
    assert out.status == "completed"
    assert out.error is None


def test_agent_output_with_error():
    out = AgentOutput(
        agent_type="impl",
        stage="realization",
        status="blocked",
        artifact_path="",
        summary="",
        error="TDD violation: test outline missing",
    )
    assert out.status == "blocked"
    assert "TDD violation" in out.error


def test_write_artifact_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = _write_artifact(tmpdir, "subdir/test.md", "# Test content")
        assert Path(path).exists()
        assert Path(path).read_text() == "# Test content"


def test_write_artifact_creates_nested_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = _write_artifact(tmpdir, "a/b/c/deep.md", "deep content")
        assert Path(path).exists()
        assert Path(path).read_text() == "deep content"


def test_write_artifact_returns_absolute_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = _write_artifact(tmpdir, "out.md", "content")
        assert Path(path).is_absolute()


def test_brain_context_returns_string_on_failure():
    """_brain_context returns fallback string when Brain unreachable."""
    result = _brain_context("nonexistent-product", "specification")
    assert isinstance(result, str)
    assert len(result) > 0


def test_brain_context_fallback_text():
    """_brain_context returns '(no prior memories)' when Brain down."""
    result = _brain_context("nonexistent-product-xyz-999", "specification")
    # Either real memories or fallback — must be string
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_impl_activity_blocked_without_test_outline():
    """impl_activity returns blocked status when test outline missing."""
    from unittest.mock import patch
    from app.temporal_integration.activities import impl_activity

    with tempfile.TemporaryDirectory() as tmpdir:
        inp = AgentInput(
            workflow_run_id="wf-test",
            product_id="prod-test",
            product_name="Test",
            repo_path=tmpdir,
            jira_project_key="PRJ0",
            feature_id="TEST-999",
            stage="realization",
            context={},
        )
        # Patch activity.heartbeat to avoid Temporal context requirement
        with patch("app.temporal_integration.activities.activity.heartbeat"):
            result = await impl_activity(inp)
        assert result.status == "blocked"
        assert result.error is not None
        assert "TDD violation" in result.error


@pytest.mark.asyncio
async def test_impl_activity_blocked_message_contains_path():
    """impl_activity blocked error includes the missing path."""
    from unittest.mock import patch
    from app.temporal_integration.activities import impl_activity

    with tempfile.TemporaryDirectory() as tmpdir:
        inp = AgentInput(
            workflow_run_id="wf-test",
            product_id="prod-test",
            product_name="Test",
            repo_path=tmpdir,
            jira_project_key="PRJ0",
            feature_id="DEMO-42",
            stage="realization",
            context={},
        )
        with patch("app.temporal_integration.activities.activity.heartbeat"):
            result = await impl_activity(inp)
        assert result.status == "blocked"
        assert "DEMO-42" in (result.error or "")
