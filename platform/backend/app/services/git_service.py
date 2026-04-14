"""Git integration service — PRJ0-54.

Provides synchronous helpers (Temporal thread-pool safe) for:
  - create_branch  : checkout -b feature/{ticket_id}
  - commit_artifact: stage + commit specified files
  - push_branch    : push origin {branch} (graceful fail when no remote)
  - create_pr      : GitHub REST API PR creation

All functions log warnings and return None/False on failure — they never
raise so a git misconfiguration cannot break a Temporal workflow.

Env vars consumed (all optional — operations degrade gracefully):
  GITHUB_TOKEN            : personal access token with repo scope
  GITHUB_REPO_OWNER       : org or user name (e.g. "my-org")
  GITHUB_REPO_NAME        : repository name  (e.g. "my-product")
  GITHUB_DEFAULT_BASE_BRANCH : base branch for PRs (default: "main")
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], cwd: str) -> tuple[bool, str]:
    """Run a git command; returns (success, stdout/stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            logger.warning("git cmd failed %s: %s", cmd, result.stderr.strip())
            return False, result.stderr.strip()
        return True, result.stdout.strip()
    except FileNotFoundError:
        logger.warning("git not found in PATH — skipping git op")
        return False, "git not found"
    except subprocess.TimeoutExpired:
        logger.warning("git cmd timed out: %s", cmd)
        return False, "timeout"
    except Exception as exc:
        logger.warning("git cmd exception %s: %s", cmd, exc)
        return False, str(exc)


def _is_git_repo(repo_path: str) -> bool:
    ok, _ = _run(["git", "rev-parse", "--is-inside-work-tree"], repo_path)
    return ok


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def branch_name(ticket_id: str) -> str:
    """Canonical branch name for a ticket: feature/PRJ0-54."""
    return f"feature/{ticket_id}"


def create_branch(repo_path: str, ticket_id: str) -> Optional[str]:
    """Checkout or create branch feature/{ticket_id}.

    Returns branch name on success, None on failure.
    Idempotent: if branch already exists, checks it out.
    """
    if not _is_git_repo(repo_path):
        logger.warning("Not a git repo: %s — skipping create_branch", repo_path)
        return None

    bname = branch_name(ticket_id)

    # Try to switch to existing branch first
    ok, _ = _run(["git", "checkout", bname], repo_path)
    if ok:
        logger.info("Checked out existing branch %s", bname)
        return bname

    # Create new branch from current HEAD
    ok, out = _run(["git", "checkout", "-b", bname], repo_path)
    if ok:
        logger.info("Created branch %s in %s", bname, repo_path)
        return bname

    logger.warning("create_branch failed for %s: %s", bname, out)
    return None


def commit_artifact(
    repo_path: str,
    artifact_paths: list[str],
    ticket_id: str,
    message: str | None = None,
) -> bool:
    """Stage artifact_paths and commit with a ticket-referenced message.

    artifact_paths: absolute or relative-to-repo_path file paths.
    Returns True on success.
    """
    if not _is_git_repo(repo_path):
        logger.warning("Not a git repo: %s — skipping commit", repo_path)
        return False

    if not artifact_paths:
        return False

    # Normalise to paths relative to repo root
    repo = Path(repo_path).resolve()
    rel_paths: list[str] = []
    for p in artifact_paths:
        ap = Path(p).resolve()
        try:
            rel_paths.append(str(ap.relative_to(repo)))
        except ValueError:
            rel_paths.append(p)  # keep as-is if outside repo

    # Stage files
    ok, out = _run(["git", "add", "--"] + rel_paths, repo_path)
    if not ok:
        logger.warning("git add failed: %s", out)
        return False

    # Check if there's anything staged
    ok_status, staged = _run(["git", "diff", "--cached", "--name-only"], repo_path)
    if not staged:
        logger.info("Nothing to commit for %s", ticket_id)
        return True  # not an error

    commit_msg = message or f"{ticket_id}: agent-generated artifact"
    ok, out = _run(["git", "commit", "-m", commit_msg], repo_path)
    if ok:
        logger.info("Committed artifact for %s", ticket_id)
        return True

    logger.warning("git commit failed for %s: %s", ticket_id, out)
    return False


def push_branch(repo_path: str, ticket_id: str) -> bool:
    """Push feature/{ticket_id} to origin.

    Returns True on success. Graceful fail when no remote configured.
    """
    if not _is_git_repo(repo_path):
        return False

    bname = branch_name(ticket_id)
    ok, out = _run(["git", "push", "origin", bname, "--set-upstream"], repo_path)
    if ok:
        logger.info("Pushed branch %s", bname)
        return True

    # Common non-fatal scenarios
    if "remote" in out.lower() or "Repository not found" in out:
        logger.warning("push skipped — no remote configured or auth failed: %s", out)
    else:
        logger.warning("push failed for %s: %s", bname, out)
    return False


def create_pr(
    ticket_id: str,
    title: str,
    body: str,
    base_branch: str | None = None,
) -> Optional[str]:
    """Create a GitHub PR for feature/{ticket_id} → base_branch.

    Returns the PR HTML URL on success, None on failure.
    Requires env vars: GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME.
    """
    token = os.getenv("GITHUB_TOKEN", "")
    owner = os.getenv("GITHUB_REPO_OWNER") or os.getenv("GITHUB_ORG", "")
    repo = os.getenv("GITHUB_REPO_NAME", "")
    base = base_branch or os.getenv("GITHUB_DEFAULT_BASE_BRANCH") or os.getenv("GITHUB_DEFAULT_BRANCH", "main")

    if not (token and owner and repo):
        logger.warning(
            "GitHub PR skipped — missing env vars (GITHUB_TOKEN / GITHUB_REPO_OWNER / GITHUB_REPO_NAME)"
        )
        return None

    try:
        import httpx  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("httpx not installed — cannot create PR")
        return None

    bname = branch_name(ticket_id)
    payload = {
        "title": title,
        "body": body,
        "head": bname,
        "base": base,
        "draft": False,
    }

    try:
        r = httpx.post(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30,
        )
        if r.status_code in (200, 201):
            pr_url = r.json().get("html_url", "")
            logger.info("PR created: %s", pr_url)
            return pr_url
        elif r.status_code == 422:
            # PR already exists — extract existing PR URL if possible
            existing = r.json().get("errors", [])
            logger.warning("PR already exists for %s: %s", bname, existing)
            return None
        else:
            logger.warning("GitHub PR creation failed %s: %s", r.status_code, r.text[:200])
            return None
    except Exception as exc:
        logger.warning("create_pr exception for %s: %s", ticket_id, exc)
        return None
