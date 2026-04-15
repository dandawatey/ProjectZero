#!/usr/bin/env python3
"""
bootstrap-agent.py — Agentic product bootstrap using Claude claude-opus-4-6 + tool use.

Usage:
    python scripts/bootstrap-agent.py "bootstrap i-comply for iSourceInnovations"
    python scripts/bootstrap-agent.py --skip=jira,confluence "bootstrap my-api"
    python scripts/bootstrap-agent.py --dry-run "bootstrap demo-app"

The agent reasons through each bootstrap step, calls tools to execute actions,
handles errors intelligently (e.g., suggests alternative JIRA key if taken),
and streams all progress to the terminal.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import urllib.request
import urllib.error
import base64
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.theme import Theme

# ── Terminal output ────────────────────────────────────────────────────────────
THEME = Theme({
    "tool":    "bold cyan",
    "ok":      "bold green",
    "warn":    "bold yellow",
    "error":   "bold red",
    "step":    "bold white",
    "dim":     "dim white",
    "think":   "italic dim cyan",
})
console = Console(theme=THEME, highlight=False)

def p_step(msg: str):  console.print(f"[step]▶[/step] {msg}")
def p_ok(msg: str):    console.print(f"[ok]✓[/ok] {msg}")
def p_warn(msg: str):  console.print(f"[warn]⚠[/warn]  {msg}")
def p_err(msg: str):   console.print(f"[error]✗[/error] {msg}")
def p_tool(msg: str):  console.print(f"[tool]⚙[/tool]  {msg}")
def p_think(msg: str): console.print(f"[think]{msg}[/think]")
def p_dim(msg: str):   console.print(f"[dim]{msg}[/dim]")

# ── Factory paths ──────────────────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).resolve().parent.parent
PARENT_DIR   = FACTORY_ROOT.parent

# ── Env helpers ───────────────────────────────────────────────────────────────
def load_env(path: Path) -> dict[str, str]:
    """Safe line-by-line .env parser — ignores comments and bare words."""
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line)
        if m:
            key, val = m.group(1), m.group(2)
            val = val.strip('"').strip("'")
            env[key] = val
    return env

FACTORY_ENV = load_env(FACTORY_ROOT / ".env")

def env(key: str, default: str = "") -> str:
    return FACTORY_ENV.get(key, os.environ.get(key, default))

# ── GitHub token (env → keychain fallback) ────────────────────────────────────
def get_github_token() -> str:
    token = env("GITHUB_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if line.startswith("password="):
                return line[9:]
    except Exception:
        pass
    return ""

GH_TOKEN = get_github_token()

# ── HTTP helpers ───────────────────────────────────────────────────────────────
def _basic_auth(user: str, token: str) -> str:
    return base64.b64encode(f"{user}:{token}".encode()).decode()

def http_get(url: str, headers: dict) -> tuple[int, dict | list]:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}

def http_post(url: str, headers: dict, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = {}
        try: body = json.loads(e.read())
        except Exception: pass
        return e.code, body

# ── Tool implementations ───────────────────────────────────────────────────────

def _tool_validate_factory() -> dict:
    issues = []
    for key in ["ANTHROPIC_API_KEY", "JIRA_BASE_URL", "CONFLUENCE_BASE_URL"]:
        if not env(key):
            issues.append(f"missing {key}")
    if not GH_TOKEN:
        issues.append("missing GITHUB_TOKEN (env or keychain)")
    scaffold = FACTORY_ROOT / ".claude" / "templates" / "product-skeleton"
    if not scaffold.exists():
        issues.append(f"scaffold missing: {scaffold}")
    if issues:
        return {"ok": False, "issues": issues}
    return {"ok": True, "factory_root": str(FACTORY_ROOT), "parent_dir": str(PARENT_DIR)}


def _tool_read_factory_env() -> dict:
    safe = {k: v for k, v in FACTORY_ENV.items()
            if k not in ("GITHUB_TOKEN", "JIRA_API_TOKEN", "CONFLUENCE_API_TOKEN",
                         "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "DATABASE_URL",
                         "REDIS_PASSWORD", "REDIS_URL")}
    safe["GITHUB_TOKEN_PRESENT"] = bool(GH_TOKEN)
    safe["JIRA_API_TOKEN_PRESENT"] = bool(env("JIRA_API_TOKEN"))
    safe["CONFLUENCE_API_TOKEN_PRESENT"] = bool(env("CONFLUENCE_API_TOKEN"))
    safe["ANTHROPIC_API_KEY_PRESENT"] = bool(env("ANTHROPIC_API_KEY"))
    return safe


def _tool_check_github_repo(owner: str, name: str) -> dict:
    code, body = http_get(
        f"https://api.github.com/repos/{owner}/{name}",
        {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    )
    if code == 200:
        return {"exists": True, "clone_url": body.get("clone_url", ""),
                "html_url": body.get("html_url", ""), "default_branch": body.get("default_branch", "main")}
    return {"exists": False}


def _tool_create_github_repo(owner: str, name: str, description: str, is_org: bool) -> dict:
    headers = {"Authorization": f"token {GH_TOKEN}",
               "Accept": "application/vnd.github.v3+json",
               "Content-Type": "application/json"}
    payload = {"name": name, "description": description, "private": True, "auto_init": True}
    url = f"https://api.github.com/orgs/{owner}/repos" if is_org else "https://api.github.com/user/repos"
    code, body = http_post(url, headers, payload)
    if code in (200, 201):
        return {"ok": True, "clone_url": body.get("clone_url", ""),
                "html_url": body.get("html_url", ""), "full_name": body.get("full_name", f"{owner}/{name}")}
    return {"ok": False, "status": code, "error": body.get("message", str(body))}


def _tool_clone_repo(clone_url: str, product_root: str) -> dict:
    root = Path(product_root)
    if root.exists() and (root / ".git").exists():
        return {"ok": True, "skipped": True, "reason": "already cloned"}
    if root.exists() and any(root.iterdir()):
        return {"ok": False, "error": f"{product_root} exists and is non-empty, non-git directory"}
    auth_url = re.sub(r"https://", f"https://{GH_TOKEN}@", clone_url)
    result = subprocess.run(
        ["git", "clone", auth_url, str(root)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return {"ok": True, "product_root": str(root)}
    return {"ok": False, "error": result.stderr.strip()}


def _tool_inject_scaffold(product_root: str) -> dict:
    skeleton = FACTORY_ROOT / ".claude" / "templates" / "product-skeleton"
    dest_claude = Path(product_root) / ".claude"
    if not skeleton.exists():
        return {"ok": False, "error": f"skeleton not found: {skeleton}"}
    copied = []
    for src in skeleton.rglob("*"):
        if src.is_file():
            rel = src.relative_to(skeleton)
            dst = dest_claude / rel
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied.append(str(rel))
    return {"ok": True, "files_copied": len(copied), "files": copied[:10]}


def _tool_check_jira_project(key: str) -> dict:
    user = env("JIRA_USER_EMAIL")
    token = env("JIRA_API_TOKEN")
    base = env("JIRA_BASE_URL").rstrip("/")
    code, body = http_get(
        f"{base}/rest/api/3/project/{key}",
        {"Authorization": f"Basic {_basic_auth(user, token)}",
         "Accept": "application/json"}
    )
    if code == 200:
        return {"exists": True, "key": key, "name": body.get("name", "")}
    return {"exists": False, "status": code}


def _tool_create_jira_project(key: str, name: str, description: str) -> dict:
    user = env("JIRA_USER_EMAIL")
    token = env("JIRA_API_TOKEN")
    base = env("JIRA_BASE_URL").rstrip("/")

    # Get account ID
    code, me = http_get(
        f"{base}/rest/api/3/myself",
        {"Authorization": f"Basic {_basic_auth(user, token)}", "Accept": "application/json"}
    )
    if code != 200:
        return {"ok": False, "error": f"cannot fetch account ID: {code}"}
    account_id = me.get("accountId", "")

    payload = {
        "key": key, "name": name, "description": description,
        "projectTypeKey": "software", "projectTemplateKey":
            "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic",
        "leadAccountId": account_id,
        "assigneeType": "UNASSIGNED",
    }
    headers = {"Authorization": f"Basic {_basic_auth(user, token)}",
               "Accept": "application/json", "Content-Type": "application/json"}
    code, body = http_post(f"{base}/rest/api/3/project", headers, payload)
    if code in (200, 201):
        return {"ok": True, "key": key, "id": body.get("id", ""), "self": body.get("self", "")}
    return {"ok": False, "status": code, "error": body.get("errorMessages", [str(body)])}


def _tool_check_confluence_space(key: str) -> dict:
    user = env("JIRA_USER_EMAIL")
    token = env("CONFLUENCE_API_TOKEN")
    base = env("CONFLUENCE_BASE_URL").rstrip("/")
    code, body = http_get(
        f"{base}/rest/api/space/{key}",
        {"Authorization": f"Basic {_basic_auth(user, token)}",
         "Accept": "application/json"}
    )
    if code == 200:
        return {"exists": True, "key": key, "name": body.get("name", "")}
    return {"exists": False, "status": code}


def _tool_create_confluence_space(key: str, name: str, description: str) -> dict:
    user = env("JIRA_USER_EMAIL")
    token = env("CONFLUENCE_API_TOKEN")
    base = env("CONFLUENCE_BASE_URL").rstrip("/")
    payload = {"key": key, "name": name,
               "description": {"plain": {"value": description, "representation": "plain"}}}
    headers = {"Authorization": f"Basic {_basic_auth(user, token)}",
               "Accept": "application/json", "Content-Type": "application/json"}
    code, body = http_post(f"{base}/rest/api/space", headers, payload)
    if code in (200, 201):
        return {"ok": True, "key": key, "id": body.get("id", "")}
    return {"ok": False, "status": code, "error": body.get("message", str(body))}


def _tool_create_project_structure(product_root: str, product_name: str) -> dict:
    root = Path(product_root)
    dirs = [
        "src", "tests", "docs",
        ".github/workflows",
        ".claude/memory", ".claude/decisions",
    ]
    created = []
    for d in dirs:
        p = root / d
        p.mkdir(parents=True, exist_ok=True)
        gi = p / ".gitkeep"
        if not gi.exists():
            gi.touch()
            created.append(d)

    # README stub
    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(f"# {product_name}\n\n> Bootstrapped by ProjectZeroFactory\n")
        created.append("README.md")

    return {"ok": True, "dirs_created": created}


def _tool_write_product_env(product_root: str, config: dict) -> dict:
    root = Path(product_root)
    if not (root / ".git").exists():
        return {"ok": False, "error": f"not a git repo: {product_root}"}
    if root == FACTORY_ROOT:
        return {"ok": False, "error": "REFUSE: product_root == factory_root"}

    lines = [
        f"PRODUCT_NAME={config.get('product_name', '')}",
        f"PROJECT_MODE={config.get('project_mode', 'greenfield')}",
        f"PRODUCT_ROOT={product_root}",
        f"GITHUB_REPO={config.get('github_repo', '')}",
        f"JIRA_ENABLED={str(config.get('jira_enabled', True)).lower()}",
        f"CONFLUENCE_ENABLED={str(config.get('confluence_enabled', True)).lower()}",
    ]
    if config.get("jira_project_key"):
        lines.append(f"JIRA_PROJECT_KEY={config['jira_project_key']}")
    if config.get("confluence_space_key"):
        lines.append(f"CONFLUENCE_SPACE_KEY={config['confluence_space_key']}")

    # Copy integration keys from factory env
    for key in ["JIRA_BASE_URL", "JIRA_API_TOKEN", "JIRA_USER_EMAIL",
                "CONFLUENCE_BASE_URL", "CONFLUENCE_API_TOKEN",
                "GITHUB_TOKEN", "ANTHROPIC_API_KEY",
                "DATABASE_URL", "REDIS_URL", "REDIS_PASSWORD"]:
        val = env(key)
        if val:
            lines.append(f"{key}={val}")

    env_path = root / ".env"
    env_path.write_text("\n".join(lines) + "\n")

    # .gitignore
    gi = root / ".gitignore"
    content = gi.read_text() if gi.exists() else ""
    if ".env" not in content.splitlines():
        with gi.open("a") as f:
            f.write("\n.env\n")

    return {"ok": True, "path": str(env_path)}


def _tool_git_commit_push(product_root: str, github_repo_full: str) -> dict:
    root = Path(product_root)
    auth_remote = f"https://{GH_TOKEN}@github.com/{github_repo_full}.git"

    def run(cmd):
        return subprocess.run(cmd, cwd=root, capture_output=True, text=True)

    # Ensure remote set with auth
    run(["git", "remote", "set-url", "origin", auth_remote])

    # Pull to avoid diverged histories (auto_init creates a commit)
    run(["git", "pull", "origin", "HEAD", "--rebase", "--allow-unrelated-histories", "-q"])

    # Stage and commit
    run(["git", "add", "-A"])
    r = run(["git", "commit", "-m", "chore: inject factory scaffold\n\nBootstrapped by ProjectZeroFactory bootstrap-agent"])
    if r.returncode != 0 and "nothing to commit" not in r.stdout + r.stderr:
        return {"ok": False, "error": r.stderr.strip()}

    # Push
    r = run(["git", "push", "origin", "HEAD"])
    if r.returncode != 0:
        return {"ok": False, "error": r.stderr.strip()}

    return {"ok": True}


def _tool_update_workspace(product_root: str, product_name: str) -> dict:
    ws_name = PARENT_DIR.name.lower().replace(" ", "-") + ".code-workspace"
    ws_path = PARENT_DIR / ws_name
    root = Path(product_root)

    # Load or seed workspace
    if ws_path.exists():
        ws = json.loads(ws_path.read_text())
    else:
        ws = {"folders": [], "settings": {}, "tasks": {"version": "2.0.0", "tasks": []}}

    # Check if already present
    existing_paths = {f.get("path") for f in ws.get("folders", [])}
    if str(root) in existing_paths:
        return {"ok": True, "skipped": True, "reason": "already in workspace"}

    # Build folder entries
    emoji = "📦"
    # Product root only — src/tests/docs are subfolders within it, not separate roots
    new_folders = [{"name": f"{emoji} {product_name}", "path": str(root)}]

    ws["folders"].extend(new_folders)

    # Window title
    parent_title = PARENT_DIR.name
    ws.setdefault("settings", {})["window.title"] = f"{parent_title} — ${{activeEditorShort}}"
    ws["settings"].setdefault("editor.formatOnSave", True)
    ws["settings"].setdefault("explorer.sortOrder", "type")
    ws["settings"].setdefault("files.exclude", {
        "**/__pycache__": True, "**/.pytest_cache": True, "**/node_modules": True
    })

    # Tasks
    ws.setdefault("tasks", {"version": "2.0.0", "tasks": []})
    existing_labels = {t.get("label") for t in ws["tasks"].get("tasks", [])}
    for label, cmd, detail in [
        (f"{product_name}: /spec",      "claude --print '/spec'",      "Generate stories from PRD"),
        (f"{product_name}: /implement", "claude --print '/implement'", "Build next ticket (TDD)"),
        (f"{product_name}: /check",     "claude --print '/check'",     "Run quality gates"),
    ]:
        if label not in existing_labels:
            ws["tasks"]["tasks"].append({
                "label": label, "type": "shell",
                "command": cmd, "detail": detail
            })

    ws_path.write_text(json.dumps(ws, indent=2))
    return {"ok": True, "workspace_file": str(ws_path), "folders_added": [f["name"] for f in new_folders]}


def _tool_open_in_vscode(product_root: str) -> dict:
    ws_name = PARENT_DIR.name.lower().replace(" ", "-") + ".code-workspace"
    ws_path = PARENT_DIR / ws_name

    # Try bundled VS Code CLI
    vscode_cli_paths = [
        "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
        "/usr/local/bin/code",
        shutil.which("code") or "",
    ]
    cli = next((p for p in vscode_cli_paths if p and Path(p).exists()), None)

    if cli:
        r = subprocess.run([cli, "--add", product_root], capture_output=True, text=True)
        if r.returncode == 0:
            return {"ok": True, "method": "code --add", "cli": cli}

    # Fallback: open workspace file
    if ws_path.exists():
        r = subprocess.run(["open", str(ws_path)], capture_output=True, text=True)
        if r.returncode == 0:
            return {"ok": True, "method": "open workspace file", "path": str(ws_path)}

    return {"ok": False, "error": "VS Code CLI not found; open workspace manually",
            "workspace_file": str(ws_path)}


def _tool_setup_design_system(product_root: str, framework: str, pm: str,
                               skip_storybook: bool, skip_framer: bool,
                               brand_color: str) -> dict:
    """Install design system: tokens, Framer Motion, Storybook, base components."""
    root = Path(product_root)
    ds = root / "src" / "design-system"

    # ── Detect framework + pm if not provided ──────────────────────────────────
    if not framework or framework == "auto":
        pkg_json = root / "package.json"
        framework = "react"  # default
        if pkg_json.exists():
            deps = json.loads(pkg_json.read_text()).get("dependencies", {})
            if "next" in deps:       framework = "next"
            elif "vue" in deps:      framework = "vue"
            elif "svelte" in deps:   framework = "svelte"

    if not pm or pm == "auto":
        pm = "npm"
        if (root / "pnpm-lock.yaml").exists():  pm = "pnpm"
        elif (root / "yarn.lock").exists():      pm = "yarn"
        elif (root / "bun.lockb").exists():      pm = "bun"

    storybook_fw = {
        "next":   "@storybook/nextjs",
        "react":  "@storybook/react-vite",
        "vue":    "@storybook/vue3-vite",
        "svelte": "@storybook/svelte-vite",
    }.get(framework, "@storybook/react-vite")

    created = []

    # ── 1. Design tokens ──────────────────────────────────────────────────────
    ds.mkdir(parents=True, exist_ok=True)
    tokens_file = ds / "tokens.ts"
    if not tokens_file.exists():
        tokens_file.write_text(f'''\
// Design tokens — generated by ProjectZeroFactory bootstrap
// Brand seed: {brand_color or "#0ea5e9"}

export const colors = {{
  brand: {{
    50: "#f0f9ff", 100: "#e0f2fe", 200: "#bae6fd", 300: "#7dd3fc",
    400: "#38bdf8", 500: "{brand_color or "#0ea5e9"}", 600: "#0284c7",
    700: "#0369a1", 800: "#075985", 900: "#0c4a6e", 950: "#082f49",
  }},
  neutral: {{
    0: "#ffffff", 50: "#f8fafc", 100: "#f1f5f9", 200: "#e2e8f0",
    300: "#cbd5e1", 400: "#94a3b8", 500: "#64748b", 600: "#475569",
    700: "#334155", 800: "#1e293b", 900: "#0f172a", 950: "#020617",
  }},
  semantic: {{
    success: {{ bg: "#f0fdf4", text: "#166534", border: "#bbf7d0" }},
    warning: {{ bg: "#fffbeb", text: "#92400e", border: "#fde68a" }},
    error:   {{ bg: "#fef2f2", text: "#991b1b", border: "#fecaca" }},
    info:    {{ bg: "#eff6ff", text: "#1e40af", border: "#bfdbfe" }},
  }},
}}

export const typography = {{
  fontFamily: {{
    sans:  "var(--font-sans, ui-sans-serif, system-ui, sans-serif)",
    mono:  "var(--font-mono, ui-monospace, \\"Cascadia Code\\", monospace)",
  }},
  fontSize: {{
    xs: ["0.75rem", {{ lineHeight: "1rem" }}],
    sm: ["0.875rem", {{ lineHeight: "1.25rem" }}],
    base: ["1rem", {{ lineHeight: "1.5rem" }}],
    lg: ["1.125rem", {{ lineHeight: "1.75rem" }}],
    xl: ["1.25rem", {{ lineHeight: "1.75rem" }}],
    "2xl": ["1.5rem", {{ lineHeight: "2rem" }}],
    "3xl": ["1.875rem", {{ lineHeight: "2.25rem" }}],
    "4xl": ["2.25rem", {{ lineHeight: "2.5rem" }}],
  }},
  fontWeight: {{ normal: "400", medium: "500", semibold: "600", bold: "700" }},
}}

export const spacing = {{
  px: "1px", 0: "0", 0.5: "0.125rem", 1: "0.25rem",
  2: "0.5rem", 3: "0.75rem", 4: "1rem", 5: "1.25rem",
  6: "1.5rem", 8: "2rem", 10: "2.5rem", 12: "3rem",
  16: "4rem", 20: "5rem", 24: "6rem", 32: "8rem",
}}

export const radii = {{
  none: "0", sm: "0.125rem", base: "0.25rem", md: "0.375rem",
  lg: "0.5rem", xl: "0.75rem", "2xl": "1rem", full: "9999px",
}}

export const shadows = {{
  sm:   "0 1px 2px 0 rgb(0 0 0 / 0.05)",
  base: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
  md:   "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
  lg:   "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
  xl:   "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
  none: "none",
}}

export const zIndex = {{
  base: 0, raised: 1, dropdown: 10, sticky: 20,
  overlay: 30, modal: 40, popover: 50, toast: 60,
}}

export const breakpoints = {{
  sm: "640px", md: "768px", lg: "1024px", xl: "1280px", "2xl": "1536px",
}}
''')
        created.append("src/design-system/tokens.ts")

    # ── 2. Framer Motion variants ─────────────────────────────────────────────
    if not skip_framer:
        motion_file = ds / "motion.ts"
        if not motion_file.exists():
            motion_file.write_text('''\
// Framer Motion variants — generated by ProjectZeroFactory bootstrap
import type { Variants, Transition } from "framer-motion"

export const transitions = {
  fast:   { type: "tween", duration: 0.15, ease: "easeOut" } satisfies Transition,
  base:   { type: "tween", duration: 0.25, ease: "easeOut" } satisfies Transition,
  slow:   { type: "tween", duration: 0.4,  ease: "easeInOut" } satisfies Transition,
  spring: { type: "spring", stiffness: 400, damping: 30 } satisfies Transition,
  bounce: { type: "spring", stiffness: 500, damping: 20 } satisfies Transition,
} as const

export const fadeIn: Variants = {
  hidden:  { opacity: 0 },
  visible: { opacity: 1, transition: transitions.base },
  exit:    { opacity: 0, transition: transitions.fast },
}

export const fadeUp: Variants = {
  hidden:  { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: transitions.base },
  exit:    { opacity: 0, y: -8, transition: transitions.fast },
}

export const scaleIn: Variants = {
  hidden:  { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: transitions.spring },
  exit:    { opacity: 0, scale: 0.95, transition: transitions.fast },
}

export const slideInLeft: Variants = {
  hidden:  { opacity: 0, x: -24 },
  visible: { opacity: 1, x: 0, transition: transitions.base },
  exit:    { opacity: 0, x: 24, transition: transitions.fast },
}

export const stagger = (staggerChildren = 0.07, delayChildren = 0): Variants => ({
  hidden:  {},
  visible: { transition: { staggerChildren, delayChildren } },
})

export const buttonTap   = { scale: 0.97, transition: transitions.fast }
export const cardHover   = { y: -4, transition: transitions.base }
export const overlayBg   = { hidden: { opacity: 0 }, visible: { opacity: 1 } }

export const drawerSlide = {
  right: {
    hidden:  { x: "100%", opacity: 0 },
    visible: { x: 0, opacity: 1, transition: transitions.spring },
    exit:    { x: "100%", opacity: 0, transition: transitions.base },
  },
  bottom: {
    hidden:  { y: "100%", opacity: 0 },
    visible: { y: 0, opacity: 1, transition: transitions.spring },
    exit:    { y: "100%", opacity: 0, transition: transitions.base },
  },
}
''')
            created.append("src/design-system/motion.ts")

    # ── 3. Base component stubs ───────────────────────────────────────────────
    components_dir = ds / "components"
    components = {
        "Button": _component_button(skip_framer),
        "Input":  _component_input(),
        "Card":   _component_card(skip_framer),
        "Badge":  _component_badge(),
        "Spinner":_component_spinner(),
        "Avatar": _component_avatar(),
    }
    for name, (tsx, stories) in components.items():
        comp_dir = components_dir / name
        comp_dir.mkdir(parents=True, exist_ok=True)
        tsx_file = comp_dir / f"{name}.tsx"
        stories_file = comp_dir / f"{name}.stories.tsx"
        if not tsx_file.exists():
            tsx_file.write_text(tsx)
            created.append(f"src/design-system/components/{name}/{name}.tsx")
        if not stories_file.exists():
            stories_file.write_text(stories)
            created.append(f"src/design-system/components/{name}/{name}.stories.tsx")

    # ── 4. Barrel export ──────────────────────────────────────────────────────
    index_file = ds / "index.ts"
    if not index_file.exists():
        exports = ['export * from "./tokens"']
        if not skip_framer:
            exports.append('export * from "./motion"')
        for name in components:
            exports.append(f'export * from "./components/{name}/{name}"')
        index_file.write_text("\n".join(exports) + "\n")
        created.append("src/design-system/index.ts")

    # ── 5. Storybook config ───────────────────────────────────────────────────
    if not skip_storybook:
        sb_dir = root / ".storybook"
        sb_dir.mkdir(exist_ok=True)

        main_file = sb_dir / "main.ts"
        if not main_file.exists():
            main_file.write_text(f'''\
import type {{ StorybookConfig }} from "{storybook_fw}"

const config: StorybookConfig = {{
  stories: ["../src/**/*.stories.@(ts|tsx|mdx)"],
  addons: [
    "@storybook/addon-docs",
    "@storybook/addon-a11y",
    "@storybook/addon-themes",
    "@storybook/addon-viewport",
  ],
  framework: {{ name: "{storybook_fw}", options: {{}} }},
  docs: {{ autodocs: "tag" }},
}}
export default config
''')
            created.append(".storybook/main.ts")

        preview_file = sb_dir / "preview.tsx"
        if not preview_file.exists():
            preview_file.write_text('''\
import type { Preview } from "@storybook/react"
import { themes } from "@storybook/theming"

const preview: Preview = {
  parameters: {
    layout: "centered",
    docs: { theme: themes.dark },
    backgrounds: {
      default: "light",
      values: [
        { name: "light", value: "#ffffff" },
        { name: "dark",  value: "#0f172a" },
        { name: "brand", value: "#0ea5e9" },
      ],
    },
  },
}
export default preview
''')
            created.append(".storybook/preview.tsx")

    # ── 6. Install packages ───────────────────────────────────────────────────
    pkg_json_path = root / "package.json"
    if pkg_json_path.exists():
        pkg = json.loads(pkg_json_path.read_text())
        deps = list(pkg.get("dependencies", {}).keys()) + list(pkg.get("devDependencies", {}).keys())

        to_install = []
        to_install_dev = []

        if not skip_framer and "framer-motion" not in deps:
            to_install.append("framer-motion")
        if "clsx" not in deps:
            to_install.append("clsx")
        if "class-variance-authority" not in deps:
            to_install.append("class-variance-authority")

        if not skip_storybook:
            for pkg_name in [storybook_fw, "storybook",
                             "@storybook/addon-docs", "@storybook/addon-a11y",
                             "@storybook/addon-themes", "@storybook/addon-viewport"]:
                if pkg_name not in deps:
                    to_install_dev.append(pkg_name)

        install_results = []
        if to_install:
            pm_cmd = {"npm": ["npm", "install"], "pnpm": ["pnpm", "add"],
                      "yarn": ["yarn", "add"], "bun": ["bun", "add"]}[pm]
            r = subprocess.run(pm_cmd + to_install, cwd=root, capture_output=True, text=True, timeout=120)
            install_results.append({
                "packages": to_install,
                "ok": r.returncode == 0,
                "stderr": r.stderr[-200:] if r.returncode != 0 else "",
            })

        if to_install_dev:
            pm_cmd_dev = {"npm": ["npm", "install", "--save-dev"],
                          "pnpm": ["pnpm", "add", "-D"],
                          "yarn": ["yarn", "add", "--dev"],
                          "bun":  ["bun", "add", "-d"]}[pm]
            r = subprocess.run(pm_cmd_dev + to_install_dev, cwd=root, capture_output=True, text=True, timeout=120)
            install_results.append({
                "packages": to_install_dev,
                "ok": r.returncode == 0,
                "stderr": r.stderr[-200:] if r.returncode != 0 else "",
            })

        # Add storybook scripts to package.json
        pkg = json.loads(pkg_json_path.read_text())
        scripts = pkg.setdefault("scripts", {})
        if "storybook" not in scripts:
            scripts["storybook"] = "storybook dev -p 6006"
        if "storybook:build" not in scripts:
            scripts["storybook:build"] = "storybook build"
        pkg_json_path.write_text(json.dumps(pkg, indent=2))
        created.append("package.json (storybook scripts added)")
    else:
        install_results = [{"ok": False, "error": "No package.json found — skipped npm install"}]

    return {
        "ok": True,
        "framework": framework,
        "package_manager": pm,
        "storybook_installed": not skip_storybook,
        "framer_installed": not skip_framer,
        "files_created": created,
        "install_results": install_results if pkg_json_path.exists() else [],
    }


# ── Component templates ────────────────────────────────────────────────────────

def _component_button(skip_framer: bool) -> tuple[str, str]:
    motion_import = 'import { motion } from "framer-motion"\nimport { buttonTap } from "../../motion"\n' if not skip_framer else ""
    comp_el = "motion.button" if not skip_framer else "button"
    whiltap = "\n      whileTap={animate ? buttonTap : undefined}" if not skip_framer else ""
    animate_prop = '\n  animate?: boolean' if not skip_framer else ""
    animate_default = ', animate = true' if not skip_framer else ''

    tsx = f'''\
{motion_import}import {{ cva, type VariantProps }} from "class-variance-authority"
import {{ clsx }} from "clsx"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {{
    variants: {{
      variant: {{
        primary:     "bg-sky-600 text-white hover:bg-sky-700 focus-visible:ring-sky-500",
        secondary:   "bg-slate-100 text-slate-900 hover:bg-slate-200 focus-visible:ring-slate-400",
        ghost:       "hover:bg-slate-100 text-slate-700 focus-visible:ring-slate-400",
        outline:     "border border-slate-300 bg-transparent hover:bg-slate-50 focus-visible:ring-slate-400",
        destructive: "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
      }},
      size: {{
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
      }},
    }},
    defaultVariants: {{ variant: "primary", size: "md" }},
  }}
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {{
  loading?: boolean{animate_prop}
}}

export function Button({{
  variant, size, loading{animate_default}, children, className, ...props
}}: ButtonProps) {{
  const Comp = {comp_el} as any
  return (
    <Comp
      className={{buttonVariants({{ variant, size, className }})}}{whiltap}
      disabled={{loading || props.disabled}}
      {{...props}}
    >
      {{loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />}}
      {{children}}
    </Comp>
  )
}}
'''
    stories = '''\
import type { Meta, StoryObj } from "@storybook/react"
import { Button } from "./Button"

const meta: Meta<typeof Button> = {
  title: "Design System/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: { control: "select", options: ["primary","secondary","ghost","outline","destructive"] },
    size:    { control: "select", options: ["sm","md","lg"] },
    loading: { control: "boolean" },
    disabled:{ control: "boolean" },
  },
}
export default meta
type Story = StoryObj<typeof Button>

export const Primary:     Story = { args: { children: "Button",  variant: "primary" } }
export const Secondary:   Story = { args: { children: "Button",  variant: "secondary" } }
export const Ghost:       Story = { args: { children: "Button",  variant: "ghost" } }
export const Outline:     Story = { args: { children: "Button",  variant: "outline" } }
export const Destructive: Story = { args: { children: "Delete",  variant: "destructive" } }
export const Loading:     Story = { args: { children: "Saving…", loading: true } }
export const Disabled:    Story = { args: { children: "Button",  disabled: true } }

export const AllSizes: Story = {
  render: () => (
    <div className="flex items-center gap-3">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
}
'''
    return tsx, stories


def _component_input() -> tuple[str, str]:
    tsx = '''\
import { clsx } from "clsx"
import { forwardRef } from "react"

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\\s+/g, "-")
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-slate-700">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={clsx(
            "h-10 w-full rounded-md border px-3 text-sm transition-colors",
            "placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-offset-1",
            error
              ? "border-red-400 focus:ring-red-400"
              : "border-slate-300 focus:ring-sky-500",
            props.disabled && "cursor-not-allowed bg-slate-50 opacity-60",
            className
          )}
          {...props}
        />
        {error && <p className="text-xs text-red-600">{error}</p>}
        {hint && !error && <p className="text-xs text-slate-500">{hint}</p>}
      </div>
    )
  }
)
Input.displayName = "Input"
'''
    stories = '''\
import type { Meta, StoryObj } from "@storybook/react"
import { Input } from "./Input"

const meta: Meta<typeof Input> = {
  title: "Design System/Input",
  component: Input,
  tags: ["autodocs"],
}
export default meta
type Story = StoryObj<typeof Input>

export const Default:   Story = { args: { placeholder: "Enter text…" } }
export const WithLabel: Story = { args: { label: "Email address", placeholder: "you@example.com" } }
export const WithHint:  Story = { args: { label: "Username", hint: "3–20 characters, letters and numbers only" } }
export const WithError: Story = { args: { label: "Email", error: "Invalid email address", value: "notanemail" } }
export const Disabled:  Story = { args: { label: "Disabled", value: "Read only", disabled: true } }
'''
    return tsx, stories


def _component_card(skip_framer: bool) -> tuple[str, str]:
    motion_import = 'import { motion } from "framer-motion"\nimport { cardHover } from "../../motion"\n' if not skip_framer else ""
    tsx = f'''\
{motion_import}import {{ clsx }} from "clsx"

interface CardProps {{
  children: React.ReactNode
  className?: string
  interactive?: boolean
  padding?: "none" | "sm" | "md" | "lg"
}}

export function Card({{ children, className, interactive = false, padding = "md" }}: CardProps) {{
  const base = clsx(
    "rounded-xl border border-slate-200 bg-white shadow-sm",
    interactive && "cursor-pointer transition-shadow hover:shadow-md",
    {{ none: "", sm: "p-3", md: "p-5", lg: "p-8" }}[padding],
    className
  )
  {"return interactive ? (" if not skip_framer else "return ("}
    {"<motion.div className={base} whileHover={cardHover}>{children}</motion.div>" if not skip_framer else "<div className={base}>{children}</div>"}
  {") : (<div className={base}>{children}</div>)" if not skip_framer else ")"}
}}
'''
    stories = '''\
import type { Meta, StoryObj } from "@storybook/react"
import { Card } from "./Card"

const meta: Meta<typeof Card> = {
  title: "Design System/Card",
  component: Card,
  tags: ["autodocs"],
}
export default meta
type Story = StoryObj<typeof Card>

export const Default:     Story = { args: { children: "Card content goes here." } }
export const Interactive: Story = { args: { children: "Hover me", interactive: true } }
export const NoPadding:   Story = { args: { children: <img src="https://picsum.photos/400/200" className="rounded-xl w-full" />, padding: "none" } }
'''
    return tsx, stories


def _component_badge() -> tuple[str, str]:
    tsx = '''\
import { cva, type VariantProps } from "class-variance-authority"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        default:  "bg-slate-100 text-slate-800",
        success:  "bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20",
        warning:  "bg-yellow-50 text-yellow-800 ring-1 ring-inset ring-yellow-600/20",
        error:    "bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20",
        info:     "bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20",
        brand:    "bg-sky-100 text-sky-800",
      },
    },
    defaultVariants: { variant: "default" },
  }
)

interface BadgeProps extends VariantProps<typeof badgeVariants> {
  children: React.ReactNode
  dot?: boolean
}

export function Badge({ variant, children, dot }: BadgeProps) {
  return (
    <span className={badgeVariants({ variant })}>
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  )
}
'''
    stories = '''\
import type { Meta, StoryObj } from "@storybook/react"
import { Badge } from "./Badge"

const meta: Meta<typeof Badge> = {
  title: "Design System/Badge",
  component: Badge,
  tags: ["autodocs"],
}
export default meta
type Story = StoryObj<typeof Badge>

export const Default: Story = { args: { children: "Default" } }
export const Success: Story = { args: { children: "Active",  variant: "success", dot: true } }
export const Warning: Story = { args: { children: "Pending", variant: "warning", dot: true } }
export const Error:   Story = { args: { children: "Failed",  variant: "error",   dot: true } }
export const Info:    Story = { args: { children: "Draft",   variant: "info" } }
export const Brand:   Story = { args: { children: "New",     variant: "brand" } }
'''
    return tsx, stories


def _component_spinner() -> tuple[str, str]:
    tsx = '''\
import { clsx } from "clsx"

interface SpinnerProps {
  size?: "xs" | "sm" | "md" | "lg"
  className?: string
}

const sizes = { xs: "h-3 w-3", sm: "h-4 w-4", md: "h-6 w-6", lg: "h-8 w-8" }

export function Spinner({ size = "md", className }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={clsx(
        "inline-block animate-spin rounded-full border-2 border-current border-t-transparent",
        sizes[size],
        className
      )}
    />
  )
}
'''
    stories = '''\
import type { Meta, StoryObj } from "@storybook/react"
import { Spinner } from "./Spinner"

const meta: Meta<typeof Spinner> = {
  title: "Design System/Spinner",
  component: Spinner,
  tags: ["autodocs"],
}
export default meta
type Story = StoryObj<typeof Spinner>

export const Small:  Story = { args: { size: "sm" } }
export const Medium: Story = { args: { size: "md" } }
export const Large:  Story = { args: { size: "lg" } }
export const Colored: Story = { args: { size: "md", className: "text-sky-500" } }
'''
    return tsx, stories


def _component_avatar() -> tuple[str, str]:
    tsx = '''\
import { clsx } from "clsx"

interface AvatarProps {
  src?: string
  name?: string
  size?: "sm" | "md" | "lg" | "xl"
  className?: string
}

const sizes = { sm: "h-8 w-8 text-xs", md: "h-10 w-10 text-sm", lg: "h-12 w-12 text-base", xl: "h-16 w-16 text-lg" }

function initials(name: string) {
  return name.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase()
}

export function Avatar({ src, name, size = "md", className }: AvatarProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center justify-center rounded-full bg-slate-200 font-medium text-slate-700 overflow-hidden",
        sizes[size], className
      )}
    >
      {src
        ? <img src={src} alt={name ?? ""} className="h-full w-full object-cover" />
        : name ? initials(name) : "?"}
    </span>
  )
}
'''
    stories = '''\
import type { Meta, StoryObj } from "@storybook/react"
import { Avatar } from "./Avatar"

const meta: Meta<typeof Avatar> = {
  title: "Design System/Avatar",
  component: Avatar,
  tags: ["autodocs"],
}
export default meta
type Story = StoryObj<typeof Avatar>

export const Initials: Story = { args: { name: "Yogesh Dandawate" } }
export const Image:    Story = { args: { src: "https://i.pravatar.cc/150?img=3", name: "Avatar" } }
export const Small:    Story = { args: { name: "YD", size: "sm" } }
export const Large:    Story = { args: { name: "Yogesh Dandawate", size: "xl" } }
'''
    return tsx, stories


# ── Tool dispatch table ────────────────────────────────────────────────────────
TOOL_HANDLERS: dict[str, Any] = {
    "validate_factory":        lambda p: _tool_validate_factory(),
    "read_factory_env":        lambda p: _tool_read_factory_env(),
    "check_github_repo":       lambda p: _tool_check_github_repo(p["owner"], p["name"]),
    "create_github_repo":      lambda p: _tool_create_github_repo(p["owner"], p["name"], p["description"], p.get("is_org", False)),
    "clone_repo":              lambda p: _tool_clone_repo(p["clone_url"], p["product_root"]),
    "inject_scaffold":         lambda p: _tool_inject_scaffold(p["product_root"]),
    "check_jira_project":      lambda p: _tool_check_jira_project(p["key"]),
    "create_jira_project":     lambda p: _tool_create_jira_project(p["key"], p["name"], p.get("description", "")),
    "check_confluence_space":  lambda p: _tool_check_confluence_space(p["key"]),
    "create_confluence_space": lambda p: _tool_create_confluence_space(p["key"], p["name"], p.get("description", "")),
    "create_project_structure":lambda p: _tool_create_project_structure(p["product_root"], p["product_name"]),
    "setup_design_system":     lambda p: _tool_setup_design_system(
        p["product_root"],
        p.get("framework", "auto"),
        p.get("package_manager", "auto"),
        p.get("skip_storybook", False),
        p.get("skip_framer", False),
        p.get("brand_color", ""),
    ),
    "write_product_env":       lambda p: _tool_write_product_env(p["product_root"], p["config"]),
    "git_commit_push":         lambda p: _tool_git_commit_push(p["product_root"], p["github_repo_full"]),
    "update_workspace":        lambda p: _tool_update_workspace(p["product_root"], p["product_name"]),
    "open_in_vscode":          lambda p: _tool_open_in_vscode(p["product_root"]),
}

# ── Tool schema definitions ────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "validate_factory",
        "description": "Validate factory readiness: .env present, required keys exist, scaffold template present.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_factory_env",
        "description": "Read factory .env configuration (non-secret keys only). Returns JIRA_BASE_URL, CONFLUENCE_BASE_URL, GITHUB_ORG, etc.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "check_github_repo",
        "description": "Check if a GitHub repo exists. Returns exists:true/false, clone_url if it exists.",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "GitHub user or org name"},
                "name":  {"type": "string", "description": "Repository name"},
            },
            "required": ["owner", "name"],
        },
    },
    {
        "name": "create_github_repo",
        "description": "Create a new private GitHub repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner":       {"type": "string"},
                "name":        {"type": "string"},
                "description": {"type": "string"},
                "is_org":      {"type": "boolean", "description": "True if owner is an org (not personal account)"},
            },
            "required": ["owner", "name", "description", "is_org"],
        },
    },
    {
        "name": "clone_repo",
        "description": "Clone a GitHub repo (with token auth) into product_root directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "clone_url":    {"type": "string"},
                "product_root": {"type": "string", "description": "Absolute path to clone into"},
            },
            "required": ["clone_url", "product_root"],
        },
    },
    {
        "name": "inject_scaffold",
        "description": "Copy factory .claude/templates/product-skeleton/ into product_root/.claude/ without overwriting existing files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_root": {"type": "string"},
            },
            "required": ["product_root"],
        },
    },
    {
        "name": "check_jira_project",
        "description": "Check if a JIRA project key exists.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "JIRA project key, e.g. ICOMPLY"},
            },
            "required": ["key"],
        },
    },
    {
        "name": "create_jira_project",
        "description": "Create a new JIRA software project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key":         {"type": "string"},
                "name":        {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["key", "name"],
        },
    },
    {
        "name": "check_confluence_space",
        "description": "Check if a Confluence space key exists.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
            },
            "required": ["key"],
        },
    },
    {
        "name": "create_confluence_space",
        "description": "Create a new Confluence space.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key":         {"type": "string"},
                "name":        {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["key", "name"],
        },
    },
    {
        "name": "create_project_structure",
        "description": "Create standard directory structure: src/, tests/, docs/, .github/workflows/, .claude/memory/, README.md.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_root": {"type": "string"},
                "product_name": {"type": "string"},
            },
            "required": ["product_root", "product_name"],
        },
    },
    {
        "name": "setup_design_system",
        "description": "Install and scaffold the full design system: Tailwind-based color tokens, Framer Motion variants, 6 base components (Button/Input/Card/Badge/Spinner/Avatar) with Storybook stories, barrel export, and .storybook config. Skips files that already exist (safe for brownfield).",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_root":   {"type": "string"},
                "framework":      {"type": "string", "description": "next|react|vue|svelte|auto", "default": "auto"},
                "package_manager":{"type": "string", "description": "npm|pnpm|yarn|bun|auto",    "default": "auto"},
                "skip_storybook": {"type": "boolean", "description": "Skip Storybook install",   "default": False},
                "skip_framer":    {"type": "boolean", "description": "Skip Framer Motion",        "default": False},
                "brand_color":    {"type": "string",  "description": "Hex brand primary color",   "default": ""},
            },
            "required": ["product_root"],
        },
    },
    {
        "name": "write_product_env",
        "description": "Write product .env to PRODUCT_ROOT with all integration credentials. Validates it's a git repo and not the factory root.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_root": {"type": "string"},
                "config": {
                    "type": "object",
                    "description": "Keys: product_name, project_mode, github_repo, jira_enabled, confluence_enabled, jira_project_key (opt), confluence_space_key (opt)",
                    "properties": {
                        "product_name":        {"type": "string"},
                        "project_mode":        {"type": "string", "enum": ["greenfield", "brownfield"]},
                        "github_repo":         {"type": "string"},
                        "jira_enabled":        {"type": "boolean"},
                        "confluence_enabled":  {"type": "boolean"},
                        "jira_project_key":    {"type": "string"},
                        "confluence_space_key":{"type": "string"},
                    },
                    "required": ["product_name", "project_mode", "github_repo"],
                },
            },
            "required": ["product_root", "config"],
        },
    },
    {
        "name": "git_commit_push",
        "description": "Stage all changes, commit with scaffold message, and push to GitHub.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_root":      {"type": "string"},
                "github_repo_full":  {"type": "string", "description": "owner/repo format"},
            },
            "required": ["product_root", "github_repo_full"],
        },
    },
    {
        "name": "update_workspace",
        "description": "Add product root folder to the VS Code .code-workspace file. src/tests/docs live inside it naturally — no separate workspace roots. Also adds /spec, /implement, /check tasks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_root": {"type": "string"},
                "product_name": {"type": "string"},
            },
            "required": ["product_root", "product_name"],
        },
    },
    {
        "name": "open_in_vscode",
        "description": "Open product folder in VS Code alongside factory (code --add or open workspace).",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_root": {"type": "string"},
            },
            "required": ["product_root"],
        },
    },
]

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are the ProjectZero Bootstrap Agent. You set up new product repositories with full integration wiring.

## Factory Context
- FACTORY_ROOT: {FACTORY_ROOT}
- PARENT_DIR: {PARENT_DIR}
- Standard PRODUCT_ROOT: {PARENT_DIR}/<product-name>
- GitHub org from env: {env("GITHUB_ORG", "(not set — infer from user request or use personal account)")}
- JIRA base: {env("JIRA_BASE_URL", "(not set)")}
- Confluence base: {env("CONFLUENCE_BASE_URL", "(not set)")}

## Your Job
Bootstrap a product by executing these steps IN ORDER:
1. validate_factory — confirm env/scaffold ready
2. read_factory_env — load config (GITHUB_ORG, base URLs)
3. Resolve product_name, owner, PRODUCT_ROOT from the user request
4. check_github_repo — see if it already exists
5. create_github_repo (if not exists) OR note existing
6. clone_repo into PRODUCT_ROOT
7. inject_scaffold — copy .claude/ templates
8. check_jira_project — derive key from product name (e.g. "i-comply" → "ICOMPLY")
9. create_jira_project (if not exists) — if key taken, auto-try ICOMPLY2, etc.
10. check_confluence_space — same key logic
11. create_confluence_space (if not exists)
12. create_project_structure — src/, tests/, docs/, .github/workflows/
13. setup_design_system — tokens.ts, motion.ts, 6 base components + stories, Storybook config, install framer-motion + storybook packages
14. write_product_env — write .env to PRODUCT_ROOT
15. git_commit_push — commit scaffold and push
16. update_workspace — add to .code-workspace file
17. open_in_vscode — inject into running VS Code window

## Rules
- Derive JIRA/Confluence key: uppercase, no hyphens, max 10 chars. "i-comply" → "ICOMPLY".
- If a resource already exists, note it and continue (don't fail).
- If creation fails with key collision, try an alternative key and retry.
- PRODUCT_ROOT must differ from FACTORY_ROOT. Never write .env to factory root.
- Always complete all steps. Report final status.
- Skip integrations only if they are explicitly disabled in factory .env.
""".strip()

# ── Agent loop ─────────────────────────────────────────────────────────────────
def run_agent(user_request: str, dry_run: bool = False):
    client = anthropic.Anthropic(api_key=env("ANTHROPIC_API_KEY"))

    console.print(Panel.fit(
        f"[bold]Bootstrap Agent[/bold]\n[dim]{user_request}[/dim]",
        border_style="cyan"
    ))

    if dry_run:
        p_warn("DRY RUN — tools will be called but destructive operations skipped")

    messages: list[dict] = [{"role": "user", "content": user_request}]
    turn = 0
    max_turns = 30

    while turn < max_turns:
        turn += 1
        p_dim(f"\n── Turn {turn} ─────────────────────────────────────────")

        # Accumulate streamed response
        response_text = ""
        response_thinking = ""
        tool_uses = []
        stop_reason = None
        input_tokens = 0
        output_tokens = 0

        with client.beta.messages.stream(
            model="claude-opus-4-6",
            max_tokens=16000,
            thinking={"type": "adaptive"},
            betas=["interleaved-thinking-2025-05-14"],
            system=[{
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for event in stream:
                if hasattr(event, "type"):
                    if event.type == "content_block_delta" and hasattr(event, "delta"):
                        dt = event.delta.type
                        if dt == "thinking_delta":
                            response_thinking += event.delta.thinking
                        elif dt == "text_delta":
                            response_text += event.delta.text
                            print(event.delta.text, end="", flush=True)

            # Get final message for tool use blocks
            final = stream.get_final_message()
            stop_reason = final.stop_reason
            input_tokens = final.usage.input_tokens
            output_tokens = final.usage.output_tokens

            # Serialize content blocks to plain dicts (Pydantic → dict)
            content_dicts = []
            for block in final.content:
                if hasattr(block, "model_dump"):
                    content_dicts.append(block.model_dump())
                else:
                    content_dicts.append(dict(block))

            # Extract tool use blocks
            for block in final.content:
                if block.type == "tool_use":
                    tool_uses.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })

        if response_text:
            print()  # newline after streamed text

        if response_thinking:
            p_think(f"[thinking {len(response_thinking)} chars]")

        p_dim(f"tokens: {input_tokens} in / {output_tokens} out | stop: {stop_reason}")

        # Build assistant message — use serialized dicts (not Pydantic objects)
        messages.append({"role": "assistant", "content": content_dicts})

        # End of conversation
        if stop_reason == "end_turn" and not tool_uses:
            console.print(Rule(style="green"))
            p_ok("Bootstrap complete.")
            break

        # Process tool calls
        if tool_uses:
            tool_results = []
            for tu in tool_uses:
                name = tu["name"]
                inp = tu["input"]
                p_tool(f"{name}({', '.join(f'{k}={repr(v)[:40]}' for k, v in inp.items())})")

                if dry_run and name in ("create_github_repo", "create_jira_project",
                                        "create_confluence_space", "git_commit_push",
                                        "write_product_env", "setup_design_system"):
                    result = {"dry_run": True, "skipped": name, "would_have_used": inp}
                else:
                    handler = TOOL_HANDLERS.get(name)
                    if handler:
                        try:
                            result = handler(inp)
                        except Exception as exc:
                            result = {"ok": False, "error": str(exc)}
                    else:
                        result = {"ok": False, "error": f"unknown tool: {name}"}

                # Print result summary
                if isinstance(result, dict):
                    if result.get("ok") is False:
                        p_err(f"  → {result.get('error', result)}")
                    elif result.get("ok") is True:
                        p_ok(f"  → ok" + (f": {result.get('message', '')}" if result.get("message") else ""))
                    else:
                        p_dim(f"  → {json.dumps(result)[:120]}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": json.dumps(result),
                })

            messages.append({"role": "user", "content": tool_results})

    else:
        p_warn(f"Max turns ({max_turns}) reached.")


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Agentic product bootstrap — powered by claude-opus-4-6",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              python scripts/bootstrap-agent.py "bootstrap i-comply for iSourceInnovations"
              python scripts/bootstrap-agent.py --dry-run "bootstrap test-api for myorg"
              python scripts/bootstrap-agent.py --skip=jira "bootstrap demo-app"
        """)
    )
    parser.add_argument("request", nargs="?", help="Natural language bootstrap request")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and plan without creating external resources")
    parser.add_argument("--skip", default="",
                        help="Comma-separated integrations to skip: jira,confluence,temporal")
    args = parser.parse_args()

    if not args.request:
        parser.print_help()
        sys.exit(1)

    # Append skip hints to request so agent knows
    request = args.request
    if args.skip:
        request += f"\n\nSkip these integrations: {args.skip}"

    # Check API key
    if not env("ANTHROPIC_API_KEY"):
        p_err("ANTHROPIC_API_KEY not set in .env or environment")
        sys.exit(1)

    run_agent(request, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
