"""JIRA Feature/Epic/Story hierarchy publisher to Confluence — PRJ0-55."""
from __future__ import annotations
import logging, os
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

FEATURE_EPIC_MAP = {
    "Platform Infrastructure": {"label": "feature:infra", "slug": "infra"},
    "Integration Services": {"label": "feature:integrations", "slug": "integrations"},
    "Agent System": {"label": "feature:agents", "slug": "agents"},
    "Governance & Quality": {"label": "feature:governance", "slug": "governance"},
    "UI/UX & Product Workflow": {"label": "feature:ui", "slug": "ui"},
    "Observability & Reporting": {"label": "feature:observability", "slug": "observability"},
}

@dataclass
class StoryRow:
    key: str
    summary: str
    status: str
    status_cat: str
    points: float = 0.0
    assignee: str = "Unassigned"

@dataclass
class EpicSection:
    key: str
    summary: str
    feature_name: str
    stories: list[StoryRow] = field(default_factory=list)

@dataclass
class FeatureSection:
    name: str
    epics: list[EpicSection] = field(default_factory=list)

    @property
    def all_stories(self):
        return [s for e in self.epics for s in e.stories]

    @property
    def done_count(self):
        return sum(1 for s in self.all_stories if s.status_cat == "done")

    @property
    def total_count(self):
        return len(self.all_stories)

STATUS_ICON = {
    "done": "✅",
    "indeterminate": "🔄",
    "new": "⬜",
}

def _status_icon(status_cat: str) -> str:
    return STATUS_ICON.get(status_cat, "❓")

async def fetch_hierarchy(project_key: str = "PRJ0") -> list[FeatureSection]:
    """Fetch Feature->Epic->Story hierarchy from JIRA."""
    from app.services.jira_client import JiraClient
    import httpx
    client = JiraClient()

    async with httpx.AsyncClient() as c:
        # Get all epics
        epics = await client.project_epics(c, project_key)

        # Group epics by feature label
        feature_map: dict[str, list] = {}
        for epic in epics:
            feature_name = "Uncategorized"
            for label in epic.get("labels", []):
                if label.startswith("feature:"):
                    slug = label.split(":", 1)[1]
                    for fname, fdata in FEATURE_EPIC_MAP.items():
                        if fdata["slug"] == slug:
                            feature_name = fname
                            break
            feature_map.setdefault(feature_name, []).append(epic)

        # Build sections with stories
        features = []
        for feature_name in list(FEATURE_EPIC_MAP.keys()) + (["Uncategorized"] if "Uncategorized" in feature_map else []):
            if feature_name not in feature_map:
                continue
            feature_section = FeatureSection(name=feature_name)
            for epic in feature_map[feature_name]:
                epic_section = EpicSection(
                    key=epic["key"],
                    summary=epic["summary"],
                    feature_name=feature_name,
                )
                stories = await client.epic_stories(c, epic["key"])
                for s in stories:
                    epic_section.stories.append(StoryRow(
                        key=s["key"],
                        summary=s["summary"][:80],
                        status=s["status"],
                        status_cat=s["status_cat"],
                        points=s["points"],
                        assignee=s["assignee"],
                    ))
                feature_section.epics.append(epic_section)
            features.append(feature_section)

        return features

def _build_confluence_body(features: list[FeatureSection]) -> str:
    """Build Confluence storage-format HTML for the hierarchy page."""
    all_stories = [s for f in features for s in f.all_stories]
    total = len(all_stories)
    done = sum(1 for s in all_stories if s.status_cat == "done")
    in_prog = sum(1 for s in all_stories if s.status_cat == "indeterminate")
    blocked = total - done - in_prog

    pct = round((done / total * 100) if total else 0, 1)
    bar_filled = int(pct / 5)
    bar_empty = 20 - bar_filled
    progress_bar = "█" * bar_filled + "░" * bar_empty

    html = f"""<h1>PRJ0 — Feature Backlog &amp; Ticket Hierarchy</h1>
<p><strong>Overall Progress:</strong> [{progress_bar}] {pct}% &nbsp;|&nbsp;
✅ {done} Done &nbsp;|&nbsp; 🔄 {in_prog} In Progress &nbsp;|&nbsp; ⬜ {blocked} Todo &nbsp;|&nbsp; 📋 {total} Total</p>
<hr/>
"""
    for feature in features:
        f_done = feature.done_count
        f_total = feature.total_count
        f_pct = round((f_done / f_total * 100) if f_total else 0, 1)
        html += f"""<h2>🏗️ {feature.name} ({f_done}/{f_total} Done — {f_pct}%)</h2>
"""
        for epic in feature.epics:
            e_done = sum(1 for s in epic.stories if s.status_cat == "done")
            e_total = len(epic.stories)
            html += f"""<h3>📦 {epic.key}: {epic.summary} ({e_done}/{e_total})</h3>
<table><tbody>
<tr><th>Ticket</th><th>Summary</th><th>Status</th><th>Points</th><th>Assignee</th></tr>
"""
            for story in sorted(epic.stories, key=lambda s: s.key):
                icon = _status_icon(story.status_cat)
                html += f"<tr><td>{story.key}</td><td>{story.summary}</td><td>{icon} {story.status}</td><td>{int(story.points) if story.points else '-'}</td><td>{story.assignee}</td></tr>\n"
            html += "</tbody></table>\n"

    return html

async def publish_hierarchy_to_confluence(
    project_key: str = "PRJ0",
    space_key: str = "PR",
) -> dict:
    """Fetch JIRA hierarchy and publish to Confluence."""
    features = await fetch_hierarchy(project_key)
    body = _build_confluence_body(features)

    from app.services.confluence_client import ConfluenceClient
    client = ConfluenceClient()

    page_title = f"{project_key} — Feature Backlog & Ticket Hierarchy"

    # Try upsert (create or update)
    try:
        result = await client.upsert_page(
            title=page_title,
            body=body,
            parent_id=None,
        )
        return {"url": result.get("url", ""), "title": page_title, "features": len(features)}
    except AttributeError:
        # Fallback: use raw httpx if ConfluenceClient doesn't have upsert_page
        import httpx
        confluence_base = os.getenv("CONFLUENCE_BASE_URL", "").replace("/wiki", "")
        space = os.getenv("CONFLUENCE_SPACE_KEY", space_key)
        auth = (os.getenv("JIRA_USER_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))

        async with httpx.AsyncClient() as c:
            # Check if page exists
            search = await c.get(
                f"{confluence_base}/wiki/rest/api/content",
                params={"spaceKey": space, "title": page_title, "expand": "version"},
                auth=auth, timeout=30,
            )
            results = search.json().get("results", [])
            if results:
                page_id = results[0]["id"]
                version = results[0]["version"]["number"] + 1
                r = await c.put(
                    f"{confluence_base}/wiki/rest/api/content/{page_id}",
                    json={
                        "version": {"number": version},
                        "title": page_title,
                        "type": "page",
                        "body": {"storage": {"value": body, "representation": "storage"}},
                    },
                    auth=auth, timeout=30,
                )
            else:
                r = await c.post(
                    f"{confluence_base}/wiki/rest/api/content",
                    json={
                        "type": "page",
                        "title": page_title,
                        "space": {"key": space},
                        "body": {"storage": {"value": body, "representation": "storage"}},
                    },
                    auth=auth, timeout=30,
                )
            r.raise_for_status()
            data = r.json()
            page_id = data.get("id", "")
            url = f"{confluence_base}/wiki/spaces/{space}/pages/{page_id}"
            return {"url": url, "title": page_title, "features": len(features)}
