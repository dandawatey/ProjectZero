"""Worktree + tmux activities — isolated parallel agent execution."""

import asyncio
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from temporalio import activity

WORKTREE_BASE = os.getenv("WORKTREE_BASE", "/tmp/projectzero-worktrees")


@dataclass
class WorktreeResult:
    feature_id: str
    worktree_path: str
    branch: str
    tmux_session: str
    status: str  # created, running, completed, failed, cleaned
    error: Optional[str] = None


@activity.defn
async def create_worktree(product_path: str, feature_id: str, base_branch: str = "develop") -> WorktreeResult:
    """Create isolated git worktree for an agent to work in."""
    branch = f"feature/{feature_id}"
    worktree_path = os.path.join(WORKTREE_BASE, feature_id)
    session_name = f"agent-{feature_id}"

    # Ensure base dir exists
    Path(WORKTREE_BASE).mkdir(parents=True, exist_ok=True)

    # Create worktree
    result = subprocess.run(
        ["git", "worktree", "add", worktree_path, "-b", branch, base_branch],
        cwd=product_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Branch may already exist
        result = subprocess.run(
            ["git", "worktree", "add", worktree_path, branch],
            cwd=product_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return WorktreeResult(
                feature_id=feature_id, worktree_path=worktree_path,
                branch=branch, tmux_session=session_name,
                status="failed", error=result.stderr,
            )

    activity.logger.info(f"Worktree created: {worktree_path} on branch {branch}")

    return WorktreeResult(
        feature_id=feature_id, worktree_path=worktree_path,
        branch=branch, tmux_session=session_name, status="created",
    )


@activity.defn
async def spawn_agent_in_tmux(
    worktree_path: str,
    feature_id: str,
    agent_command: str,
) -> WorktreeResult:
    """Spawn agent in isolated tmux session within worktree."""
    session_name = f"agent-{feature_id}"

    # Kill existing session if any
    subprocess.run(["tmux", "kill-session", "-t", session_name], capture_output=True)

    # Create tmux session in worktree directory
    result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_name, "-c", worktree_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return WorktreeResult(
            feature_id=feature_id, worktree_path=worktree_path,
            branch=f"feature/{feature_id}", tmux_session=session_name,
            status="failed", error=f"tmux create failed: {result.stderr}",
        )

    # Send agent command to tmux session
    subprocess.run(
        ["tmux", "send-keys", "-t", session_name, agent_command, "Enter"],
        capture_output=True,
    )

    # Create completion signal file path
    done_file = os.path.join(worktree_path, ".agent-done")
    Path(done_file).unlink(missing_ok=True)  # clear any stale signal

    activity.logger.info(f"Agent spawned in tmux:{session_name} at {worktree_path}")

    return WorktreeResult(
        feature_id=feature_id, worktree_path=worktree_path,
        branch=f"feature/{feature_id}", tmux_session=session_name,
        status="running",
    )


@activity.defn
async def wait_for_agent_completion(
    worktree_path: str,
    feature_id: str,
    timeout_seconds: int = 1800,
) -> WorktreeResult:
    """Poll for agent completion signal file."""
    session_name = f"agent-{feature_id}"
    done_file = os.path.join(worktree_path, ".agent-done")
    elapsed = 0
    poll_interval = 10

    while elapsed < timeout_seconds:
        # Check done signal
        if Path(done_file).exists():
            activity.logger.info(f"Agent {feature_id} completed")
            return WorktreeResult(
                feature_id=feature_id, worktree_path=worktree_path,
                branch=f"feature/{feature_id}", tmux_session=session_name,
                status="completed",
            )

        # Check if tmux session still alive
        check = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
        )
        if check.returncode != 0:
            # Session died without done signal = failure
            return WorktreeResult(
                feature_id=feature_id, worktree_path=worktree_path,
                branch=f"feature/{feature_id}", tmux_session=session_name,
                status="failed", error="tmux session exited without completion signal",
            )

        activity.heartbeat(f"Waiting for agent {feature_id}... {elapsed}s/{timeout_seconds}s")
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    return WorktreeResult(
        feature_id=feature_id, worktree_path=worktree_path,
        branch=f"feature/{feature_id}", tmux_session=session_name,
        status="failed", error=f"Timeout after {timeout_seconds}s",
    )


@activity.defn
async def push_and_create_pr(
    worktree_path: str,
    feature_id: str,
    title: str,
    product_path: str,
) -> dict:
    """Push worktree branch and create PR."""
    branch = f"feature/{feature_id}"

    # Stage all changes
    subprocess.run(["git", "add", "-A"], cwd=worktree_path, capture_output=True)

    # Commit
    commit_result = subprocess.run(
        ["git", "commit", "-m", f"[{feature_id}] {title}"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    # Push
    push_result = subprocess.run(
        ["git", "push", "-u", "origin", branch],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if push_result.returncode != 0:
        return {"status": "failed", "error": push_result.stderr}

    # Create PR via gh CLI if available
    pr_result = subprocess.run(
        ["gh", "pr", "create", "--title", f"[{feature_id}] {title}",
         "--body", f"Automated PR for {feature_id}", "--base", "develop"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    return {
        "status": "pushed",
        "branch": branch,
        "pr_url": pr_result.stdout.strip() if pr_result.returncode == 0 else None,
    }


@activity.defn
async def cleanup_worktree(product_path: str, feature_id: str) -> WorktreeResult:
    """Remove worktree and kill tmux session."""
    worktree_path = os.path.join(WORKTREE_BASE, feature_id)
    session_name = f"agent-{feature_id}"

    # Kill tmux
    subprocess.run(["tmux", "kill-session", "-t", session_name], capture_output=True)

    # Remove worktree
    subprocess.run(
        ["git", "worktree", "remove", worktree_path, "--force"],
        cwd=product_path,
        capture_output=True,
    )

    return WorktreeResult(
        feature_id=feature_id, worktree_path=worktree_path,
        branch=f"feature/{feature_id}", tmux_session=session_name,
        status="cleaned",
    )


@activity.defn
async def list_active_worktrees(product_path: str) -> list[dict]:
    """List all active worktrees and their tmux sessions."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=product_path,
        capture_output=True,
        text=True,
    )

    worktrees = []
    current = {}
    for line in result.stdout.split("\n"):
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("HEAD "):
            current["head"] = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1]
        elif line == "":
            if current:
                worktrees.append(current)
            current = {}

    # Check tmux sessions
    tmux_result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True,
        text=True,
    )
    active_sessions = set(tmux_result.stdout.strip().split("\n")) if tmux_result.returncode == 0 else set()

    for wt in worktrees:
        feature_id = wt.get("branch", "").replace("refs/heads/feature/", "")
        wt["tmux_session"] = f"agent-{feature_id}" if f"agent-{feature_id}" in active_sessions else None
        wt["tmux_active"] = wt["tmux_session"] is not None

    return worktrees
