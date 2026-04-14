"""Release Activities — extracted from release_workflow.py for Temporal sandbox compliance."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass

import httpx
from temporalio import activity

from app.temporal_integration.activities import _call_claude, _write_artifact

logger = logging.getLogger(__name__)


@dataclass
class ReleaseInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    jira_project_key: str
    sprint_name: str
    version: str
    repo_path: str
    auto_approve: bool = False


def _jira_auth():
    return (os.getenv("JIRA_USER_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))

def _jira_base():
    return os.getenv("JIRA_BASE_URL", "").rstrip("/")

def _conf_base():
    return os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")

def _conf_auth():
    token = os.getenv("CONFLUENCE_API_TOKEN") or os.getenv("JIRA_API_TOKEN", "")
    return (os.getenv("JIRA_USER_EMAIL", ""), token)


@activity.defn(name="verify_release_activity")
async def verify_release_activity(inp: ReleaseInput) -> dict:
    activity.heartbeat("Verifying sprint stories complete")
    base = _jira_base()
    auth = _jira_auth()
    if not base or not all(auth):
        return {"status": "ok", "done": 0, "total": 0, "incomplete": []}
    try:
        async with httpx.AsyncClient() as c:
            jql = f'project = {inp.jira_project_key} AND sprint = "{inp.sprint_name}"'
            r = await c.get(f"{base}/rest/api/3/search",
                params={"jql": jql, "maxResults": 100, "fields": "summary,status"},
                auth=auth, timeout=30)
            issues = r.json().get("issues", []) if r.status_code == 200 else []
        done = [i for i in issues if i["fields"]["status"]["name"] == "Done"]
        incomplete = [
            {"id": i["key"], "summary": i["fields"]["summary"], "status": i["fields"]["status"]["name"]}
            for i in issues if i["fields"]["status"]["name"] != "Done"
        ]
        return {"status": "ok", "done": len(done), "total": len(issues), "incomplete": incomplete}
    except Exception as exc:
        return {"status": "error", "error": str(exc), "done": 0, "total": 0, "incomplete": []}


@activity.defn(name="generate_changelog_activity")
async def generate_changelog_activity(inp: ReleaseInput, verify: dict) -> dict:
    activity.heartbeat("Claude: generating changelog")
    try:
        output = _call_claude(
            "You are a technical writer generating release documentation.",
            f"""Product: {inp.product_name}\nVersion: {inp.version}\nSprint: {inp.sprint_name}
Stories done: {verify.get('done',0)} / {verify.get('total',0)}
Incomplete: {json.dumps(verify.get('incomplete',[])[:5])}

Generate: 1) Changelog (Keep a Changelog format) 2) Release notes 3) Known issues""")
        path = _write_artifact(inp.repo_path, f"docs/releases/{inp.version}-changelog.md", output)
        return {"status": "ok", "artifact_path": path}
    except Exception as exc:
        return {"status": "error", "error": str(exc), "artifact_path": ""}


@activity.defn(name="publish_release_activity")
async def publish_release_activity(inp: ReleaseInput, changelog: dict) -> dict:
    activity.heartbeat("Publishing release notes to Confluence")
    base = _conf_base()
    auth = _conf_auth()
    space_key = os.getenv("CONFLUENCE_SPACE_KEY", "PR")
    artifact = changelog.get("artifact_path", "")
    content = ""
    if artifact:
        try:
            from pathlib import Path
            content = Path(artifact).read_text(encoding="utf-8")
        except Exception:
            pass
    import datetime as dt
    body = f"""<h1>{inp.product_name} {inp.version}</h1>
<p><strong>Sprint:</strong> {inp.sprint_name} | <strong>Date:</strong> {dt.datetime.utcnow().strftime('%Y-%m-%d')}</p>
<ac:structured-macro ac:name="code">
  <ac:plain-text-body><![CDATA[{content[:3000]}]]></ac:plain-text-body>
</ac:structured-macro>"""
    if not base or not all(auth):
        return {"status": "skipped", "artifact_path": artifact}
    try:
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{base}/rest/api/content", auth=auth, timeout=30,
                json={"type": "page", "title": f"Release — {inp.product_name} {inp.version}",
                      "space": {"key": space_key},
                      "body": {"storage": {"value": body, "representation": "storage"}}})
            page_id = r.json().get("id") if r.status_code in (200, 201) else None
        return {"status": "ok", "page_id": page_id}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@activity.defn(name="notify_release_activity")
async def notify_release_activity(inp: ReleaseInput) -> dict:
    activity.heartbeat("Writing release to Brain")
    try:
        async with httpx.AsyncClient() as c:
            await c.post("http://localhost:8000/api/v1/brain/memories",
                json={"scope": "product", "product_id": inp.product_id, "category": "release",
                      "key": f"{inp.product_id}_release_{inp.version}",
                      "content": f"Released {inp.version} — Sprint: {inp.sprint_name}",
                      "tags": ["release", inp.version]}, timeout=10)
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
