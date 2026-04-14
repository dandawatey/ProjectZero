"""JIRA hierarchy fetcher — PRJ0-56."""
from __future__ import annotations
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")


def _auth() -> tuple[str, str]:
    return (JIRA_USER_EMAIL, JIRA_API_TOKEN)


def _headers() -> dict:
    return {"Accept": "application/json"}


def fetch_project_issues(project_key: str = "PRJ0", max_results: int = 200) -> list[dict]:
    """Fetch all issues from JIRA project. Returns list of simplified dicts."""
    if not JIRA_BASE_URL or not JIRA_USER_EMAIL or not JIRA_API_TOKEN:
        logger.warning("JIRA credentials not configured — skipping live fetch")
        return []

    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/search"
        params = {
            "jql": f"project = {project_key} ORDER BY created DESC",
            "maxResults": max_results,
            "fields": "summary,status,issuetype,parent,epic",
        }
        r = httpx.get(url, params=params, auth=_auth(), headers=_headers(), timeout=10)
        r.raise_for_status()
        issues = r.json().get("issues", [])
        return [
            {
                "key": i["key"],
                "summary": i["fields"].get("summary", ""),
                "status": i["fields"]["status"]["name"],
                "issuetype": i["fields"]["issuetype"]["name"],
                "parent": i["fields"].get("parent", {}).get("key") if i["fields"].get("parent") else None,
                "url": f"{JIRA_BASE_URL}/browse/{i['key']}",
            }
            for i in issues
        ]
    except Exception as exc:
        logger.error(f"JIRA fetch failed: {exc}")
        return []


def transition_issue(issue_key: str, transition_id: str) -> bool:
    """Transition JIRA issue to a new status."""
    if not JIRA_BASE_URL or not JIRA_USER_EMAIL or not JIRA_API_TOKEN:
        logger.warning("JIRA credentials not configured — cannot transition issue")
        return False
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
        r = httpx.post(
            url,
            json={"transition": {"id": transition_id}},
            auth=_auth(),
            headers={"Content-Type": "application/json", **_headers()},
            timeout=10,
        )
        r.raise_for_status()
        return True
    except Exception as exc:
        logger.error(f"JIRA transition failed for {issue_key}: {exc}")
        return False
