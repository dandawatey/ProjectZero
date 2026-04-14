"""Git service integration tests — PRJ0-66."""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_git_repo():
    """Create a real git repo in a temp dir."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["git", "init", tmpdir], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", tmpdir, "config", "user.email", "test@test.com"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", tmpdir, "config", "user.name", "Test"],
            check=True,
        )
        # Initial commit so HEAD exists
        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Repo")
        subprocess.run(["git", "-C", tmpdir, "add", "."], check=True)
        subprocess.run(
            ["git", "-C", tmpdir, "commit", "-m", "init"],
            check=True,
            capture_output=True,
        )
        yield tmpdir


def test_branch_name_format():
    from app.services.git_service import branch_name
    assert branch_name("PRJ0-54") == "feature/PRJ0-54"
    assert branch_name("ABC-123") == "feature/ABC-123"


def test_create_branch(temp_git_repo):
    from app.services.git_service import create_branch
    result = create_branch(temp_git_repo, "TEST-001")
    assert result == "feature/TEST-001"


def test_create_branch_idempotent(temp_git_repo):
    from app.services.git_service import create_branch
    create_branch(temp_git_repo, "TEST-002")
    result = create_branch(temp_git_repo, "TEST-002")  # second call
    assert result == "feature/TEST-002"


def test_commit_artifact(temp_git_repo):
    from app.services.git_service import create_branch, commit_artifact
    create_branch(temp_git_repo, "TEST-003")
    artifact = Path(temp_git_repo) / "test-artifact.md"
    artifact.write_text("# Test artifact content")
    result = commit_artifact(
        repo_path=temp_git_repo,
        artifact_paths=[str(artifact)],
        ticket_id="TEST-003",
        message="TEST-003: test artifact commit",
    )
    assert result is True


def test_commit_artifact_nothing_to_commit(temp_git_repo):
    from app.services.git_service import create_branch, commit_artifact
    create_branch(temp_git_repo, "TEST-004")
    # No new files — empty artifact_paths returns False
    result = commit_artifact(
        repo_path=temp_git_repo,
        artifact_paths=[],
        ticket_id="TEST-004",
    )
    assert result is False


def test_commit_artifact_no_staged_changes(temp_git_repo):
    """Staging an existing file with no changes returns True (nothing to commit = not an error)."""
    from app.services.git_service import create_branch, commit_artifact
    create_branch(temp_git_repo, "TEST-005")
    # Stage already-committed README (no new changes)
    readme = Path(temp_git_repo) / "README.md"
    result = commit_artifact(
        repo_path=temp_git_repo,
        artifact_paths=[str(readme)],
        ticket_id="TEST-005",
    )
    # Nothing staged → True (git_service treats "nothing to commit" as success)
    assert result is True


def test_create_pr_no_credentials():
    """create_pr returns None gracefully when GitHub creds not set."""
    os.environ.pop("GITHUB_TOKEN", None)
    os.environ.pop("GITHUB_REPO_OWNER", None)
    os.environ.pop("GITHUB_REPO_NAME", None)
    from app.services.git_service import create_pr
    result = create_pr("TEST-005", "Test PR", "Test body")
    assert result is None


def test_git_not_repo():
    from app.services.git_service import create_branch
    result = create_branch("/tmp", "TEST-006")
    assert result is None  # graceful fail
