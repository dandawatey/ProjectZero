"""Product repo bootstrap service — PRJ0-42.

Creates an isolated git repo for a new product with:
  - README.md
  - CLAUDE.md (inherits ProjectZeroFactory governance rules)
  - .claude/memory/ scaffold
  - docs/, src/, tests/ directories
  - .gitignore
  - .env.example

No product-specific files ever live inside ProjectZeroFactory.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

# CLAUDE.md content injected into every bootstrapped product repo
_PRODUCT_CLAUDE_MD = """\
# {product_name} — CLAUDE.md

## Factory Origin
This product was bootstrapped by **ProjectZeroFactory**.
All governance rules from ProjectZeroFactory apply here.

## Key Rules (inherited)
- All work must trace to a JIRA ticket (JIRA project: {jira_key})
- TDD: write failing test first, then implement
- Coverage >= 80% required
- No silent mutations — every change in git history
- Truthful completion only

## Stage Model
Specification → Architecture → Realization → Completion
(Managed via ProjectZeroFactory Control Tower)

## Brain
Persistent memory lives in ProjectZeroFactory Brain (Postgres).
Local `.claude/memory/` files are product-scoped snapshots.

## Caveman Mode (ACTIVE)
Respond terse like smart caveman. All technical substance stay. Only fluff die.
"""

_GITIGNORE = """\
# Dependencies
node_modules/
.venv/
__pycache__/
*.pyc

# Build output
dist/
build/
.next/

# Env
.env
*.env.local

# IDE
.idea/
.vscode/

# OS
.DS_Store
"""

_ENV_EXAMPLE = """\
# Copy to .env and fill in values
DATABASE_URL=
JIRA_BASE_URL=
JIRA_USER_EMAIL=
JIRA_API_TOKEN=
JIRA_PROJECT_KEY={jira_key}
"""

_MEMORY_SESSION = """\
# Session Log
<!-- Append entries in format: [YYYY-MM-DD HH:MM] TICKET-ID: description -->
"""

_MEMORY_DECISIONS = """\
# Architecture Decisions
<!-- Format: ## [YYYY-MM-DD] TICKET-ID: Title -->
"""

_MEMORY_PATTERNS = """\
# Reusable Patterns
<!-- Format: ## Pattern Name\\n**Context:** ...\\n**Solution:** ... -->
"""


def bootstrap_product_repo(name: str, repo_path: str, jira_project_key: str) -> dict:
    """
    Create a scaffolded git repo at repo_path for the given product.
    Returns {"success": bool, "repo_path": str, "files_created": list[str]}.
    Raises ValueError if repo_path already exists and is non-empty.
    """
    path = Path(repo_path).expanduser().resolve()

    if path.exists() and any(path.iterdir()):
        raise ValueError(f"repo_path already exists and is non-empty: {path}")

    path.mkdir(parents=True, exist_ok=True)

    jira_key = jira_project_key or name.upper().replace(" ", "")[:8]
    files_created: list[str] = []

    def write(rel: str, content: str) -> None:
        target = path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        files_created.append(rel)

    # Core files
    write("README.md", f"# {name}\n\nBootstrapped by ProjectZeroFactory.\n\nJIRA: {jira_key}\n")
    write("CLAUDE.md", _PRODUCT_CLAUDE_MD.format(product_name=name, jira_key=jira_key))
    write(".gitignore", _GITIGNORE)
    write(".env.example", _ENV_EXAMPLE.format(jira_key=jira_key))

    # .claude/memory scaffold
    write(".claude/memory/session-log.md", _MEMORY_SESSION)
    write(".claude/memory/decisions.md", _MEMORY_DECISIONS)
    write(".claude/memory/patterns.md", _MEMORY_PATTERNS)
    write(".claude/memory/blockers.md", "# Blockers\n<!-- Format: [YYYY-MM-DD] TICKET-ID: blocker → resolution -->\n")
    write(".claude/memory/learnings.md", "# Learnings\n<!-- Append after completing each ticket -->\n")

    # Directory stubs
    for stub_dir in ["docs", "src", "tests"]:
        stub_path = path / stub_dir / ".gitkeep"
        stub_path.parent.mkdir(exist_ok=True)
        stub_path.touch()
        files_created.append(f"{stub_dir}/.gitkeep")

    # Git init + initial commit
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore: bootstrap {name} via ProjectZeroFactory"],
        cwd=path,
        check=True,
        capture_output=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "ProjectZeroFactory", "GIT_AUTHOR_EMAIL": "factory@projectzero.ai",
             "GIT_COMMITTER_NAME": "ProjectZeroFactory", "GIT_COMMITTER_EMAIL": "factory@projectzero.ai"},
    )

    return {"success": True, "repo_path": str(path), "files_created": files_created}
