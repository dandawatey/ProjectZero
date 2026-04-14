"""ProductBootstrap Activities.

bootstrap_jira_activity      → create JIRA project + initial epic + stories
bootstrap_confluence_activity → create Confluence space + product home page
bootstrap_db_activity        → seed Product record + Brain memories
bootstrap_prd_activity       → Claude generates PRD from brief
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import httpx
from temporalio import activity

from app.temporal_integration.activities import _call_claude, _write_artifact

logger = logging.getLogger(__name__)


@dataclass
class BootstrapInput:
    workflow_run_id: str
    product_id: str           # slug: my-saas
    product_name: str         # display: My SaaS
    description: str          # one-paragraph brief
    owner_email: str
    repo_path: str
    jira_project_key: str     # target key e.g. MYS


# ── helpers ──────────────────────────────────────────────────────────────────

def _jira_auth() -> tuple[str, str]:
    return (os.getenv("JIRA_USER_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))

def _jira_base() -> str:
    return os.getenv("JIRA_BASE_URL", "").rstrip("/")

def _conf_base() -> str:
    return os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")

def _conf_auth() -> tuple[str, str]:
    token = os.getenv("CONFLUENCE_API_TOKEN") or os.getenv("JIRA_API_TOKEN", "")
    return (os.getenv("JIRA_USER_EMAIL", ""), token)


# ── PRD generation ───────────────────────────────────────────────────────────

_PRD_SYSTEM = """You are a product strategist at a software factory.
Given a product brief, generate a complete PRD with:
1. Problem Statement
2. Target Users (personas)
3. Goals & Success Metrics (SMART)
4. Feature List (MoSCoW prioritised)
5. Out of Scope
6. Timeline (3-sprint estimate)
7. Risks & Mitigations
8. Definition of Done

Be specific. No filler."""


@activity.defn(name="bootstrap_prd_activity")
async def bootstrap_prd_activity(inp: BootstrapInput) -> dict:
    activity.heartbeat("PRD Agent: generating product spec")
    try:
        prd = _call_claude(_PRD_SYSTEM, f"""
Product: {inp.product_name}
Brief: {inp.description}
Owner: {inp.owner_email}
JIRA key: {inp.jira_project_key}

Generate the full PRD.""")
        path = _write_artifact(inp.repo_path, "docs/PRD.md", prd)
        activity.heartbeat("PRD written")
        return {"status": "ok", "artifact_path": path, "prd_length": len(prd)}
    except Exception as exc:
        logger.error("bootstrap_prd_activity: %s", exc)
        return {"status": "error", "error": str(exc), "artifact_path": ""}


# ── JIRA bootstrap ───────────────────────────────────────────────────────────

@activity.defn(name="bootstrap_jira_activity")
async def bootstrap_jira_activity(inp: BootstrapInput) -> dict:
    activity.heartbeat("JIRA: creating project structure")
    base = _jira_base()
    auth = _jira_auth()

    if not base or not all(auth):
        return {"status": "skipped", "reason": "JIRA not configured"}

    try:
        async with httpx.AsyncClient() as c:
            # Create project
            r = await c.post(f"{base}/rest/api/3/project",
                auth=auth, timeout=30,
                json={
                    "key": inp.jira_project_key,
                    "name": inp.product_name,
                    "projectTypeKey": "software",
                    "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-scrum-template",
                    "description": inp.description,
                    "leadAccountId": None,
                })

            if r.status_code in (200, 201):
                project_id = r.json().get("id")
                activity.heartbeat("JIRA project created")
            elif r.status_code == 400 and "already exists" in r.text:
                project_id = "existing"
                activity.heartbeat("JIRA project already exists")
            else:
                return {"status": "error", "error": f"HTTP {r.status_code}: {r.text[:200]}"}

            # Create initial Epic
            epic_r = await c.post(f"{base}/rest/api/3/issue",
                auth=auth, timeout=30,
                json={
                    "fields": {
                        "project": {"key": inp.jira_project_key},
                        "summary": f"[Epic] {inp.product_name} — Sprint 1",
                        "issuetype": {"name": "Epic"},
                        "description": {
                            "type": "doc", "version": 1,
                            "content": [{"type": "paragraph", "content": [
                                {"type": "text", "text": inp.description}
                            ]}]
                        },
                    }
                })
            epic_key = epic_r.json().get("key", "") if epic_r.status_code in (200, 201) else ""
            activity.heartbeat(f"Epic created: {epic_key}")

        return {"status": "ok", "project_id": project_id, "epic_key": epic_key}
    except Exception as exc:
        logger.error("bootstrap_jira_activity: %s", exc)
        return {"status": "error", "error": str(exc)}


# ── Confluence bootstrap ──────────────────────────────────────────────────────

@activity.defn(name="bootstrap_confluence_activity")
async def bootstrap_confluence_activity(inp: BootstrapInput) -> dict:
    activity.heartbeat("Confluence: creating product home page")
    base = _conf_base()
    auth = _conf_auth()
    space_key = os.getenv("CONFLUENCE_SPACE_KEY", "PR")

    if not base or not all(auth):
        return {"status": "skipped", "reason": "Confluence not configured"}

    try:
        async with httpx.AsyncClient() as c:
            # Create product home page
            body = f"""<h1>{inp.product_name}</h1>
<p><strong>Owner:</strong> {inp.owner_email}</p>
<p><strong>JIRA Project:</strong> {inp.jira_project_key}</p>
<hr/>
<h2>Product Brief</h2>
<p>{inp.description}</p>
<h2>Pages</h2>
<ul>
  <li>PRD</li>
  <li>Architecture</li>
  <li>Sprint Plans</li>
  <li>Release Notes</li>
</ul>"""

            r = await c.post(f"{base}/rest/api/content",
                auth=auth, timeout=30,
                json={
                    "type": "page",
                    "title": f"{inp.product_name} — Home",
                    "space": {"key": space_key},
                    "body": {"storage": {"value": body, "representation": "storage"}},
                })

            if r.status_code in (200, 201):
                page_id = r.json().get("id")
                activity.heartbeat(f"Confluence page created: {page_id}")
                return {"status": "ok", "page_id": page_id}
            else:
                return {"status": "error", "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except Exception as exc:
        logger.error("bootstrap_confluence_activity: %s", exc)
        return {"status": "error", "error": str(exc)}


# ── DB bootstrap ──────────────────────────────────────────────────────────────

@activity.defn(name="bootstrap_db_activity")
async def bootstrap_db_activity(inp: BootstrapInput) -> dict:
    activity.heartbeat("DB: seeding product record")
    try:
        import httpx as _httpx
        base = os.getenv("API_BASE_URL", "http://localhost:8000")

        # Upsert product via internal API (runs in-process — localhost always available)
        async with _httpx.AsyncClient() as c:
            r = await c.post(f"{base}/api/v1/products",
                json={
                    "id": inp.product_id,
                    "name": inp.product_name,
                    "description": inp.description,
                    "jira_project_key": inp.jira_project_key,
                    "repo_path": inp.repo_path,
                    "owner_email": inp.owner_email,
                },
                timeout=10)

            if r.status_code in (200, 201, 409):
                # Seed brain memory
                await c.post(f"{base}/api/v1/brain/memories",
                    json={
                        "scope": "product",
                        "product_id": inp.product_id,
                        "category": "bootstrap",
                        "key": f"{inp.product_id}_bootstrap",
                        "content": f"Product {inp.product_name} bootstrapped. JIRA: {inp.jira_project_key}. Owner: {inp.owner_email}.",
                        "tags": ["bootstrap", "product"],
                    }, timeout=10)

                return {"status": "ok", "product_id": inp.product_id}
            else:
                return {"status": "error", "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except Exception as exc:
        logger.error("bootstrap_db_activity: %s", exc)
        return {"status": "error", "error": str(exc)}
