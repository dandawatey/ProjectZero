"""JIRA REST client for CXO dashboard metrics.

Pulls projects, sprints, issues, and derives agile metrics:
- velocity (story points completed per sprint)
- burndown (remaining points over sprint days)
- tickets per assignee (by status)
- cycle time / lead time
- issue type breakdown
- throughput
"""

from __future__ import annotations

import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

import httpx


def _auth() -> tuple[str, str]:
    return (os.getenv("JIRA_USER_EMAIL", ""), os.getenv("JIRA_API_TOKEN", ""))


def _base() -> str:
    return os.getenv("JIRA_BASE_URL", "").rstrip("/")


def _configured() -> bool:
    return bool(_base() and all(_auth()))


def _story_points_field() -> str:
    # Default JIRA Cloud story points custom field. Overridable.
    return os.getenv("JIRA_STORY_POINTS_FIELD", "customfield_10016")


class JiraClient:
    def __init__(self) -> None:
        if not _configured():
            raise RuntimeError("JIRA credentials not configured")
        self.base = _base()
        self.auth = _auth()
        self.sp_field = _story_points_field()

    async def _get(self, client: httpx.AsyncClient, path: str, params: dict | None = None) -> dict:
        r = await client.get(f"{self.base}{path}", params=params, auth=self.auth, timeout=30)
        r.raise_for_status()
        return r.json()

    # ---------------- Projects ----------------

    async def list_projects(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as c:
            data = await self._get(c, "/rest/api/3/project/search", {"maxResults": 100})
            return [
                {"key": p["key"], "name": p["name"], "id": p["id"], "lead": p.get("lead", {}).get("displayName")}
                for p in data.get("values", [])
            ]

    # ---------------- Issues (JQL) ----------------

    async def search(self, client: httpx.AsyncClient, jql: str, fields: list[str], max_results: int = 100) -> list[dict]:
        issues: list[dict] = []
        start = 0
        while True:
            data = await self._get(
                client,
                "/rest/api/3/search",
                {"jql": jql, "fields": ",".join(fields), "startAt": start, "maxResults": max_results},
            )
            issues.extend(data.get("issues", []))
            if start + max_results >= data.get("total", 0):
                break
            start += max_results
            if start > 500:  # safety cap
                break
        return issues

    # ---------------- Boards + Sprints (agile API) ----------------

    async def project_boards(self, client: httpx.AsyncClient, project_key: str) -> list[dict]:
        data = await self._get(client, "/rest/agile/1.0/board", {"projectKeyOrId": project_key})
        return data.get("values", [])

    async def board_sprints(self, client: httpx.AsyncClient, board_id: int, state: str = "closed,active") -> list[dict]:
        data = await self._get(client, f"/rest/agile/1.0/board/{board_id}/sprint", {"state": state, "maxResults": 50})
        return data.get("values", [])

    async def sprint_issues(self, client: httpx.AsyncClient, sprint_id: int) -> list[dict]:
        fields = ["summary", "status", "assignee", "issuetype", "resolutiondate", "created", self.sp_field]
        data = await self._get(
            client,
            f"/rest/agile/1.0/sprint/{sprint_id}/issue",
            {"fields": ",".join(fields), "maxResults": 200},
        )
        return data.get("issues", [])

    # ---------------- Metric derivations ----------------

    @staticmethod
    def _points(issue: dict, sp_field: str) -> float:
        v = issue.get("fields", {}).get(sp_field)
        return float(v) if isinstance(v, (int, float)) else 0.0

    @staticmethod
    def _is_done(issue: dict) -> bool:
        cat = issue.get("fields", {}).get("status", {}).get("statusCategory", {}).get("key", "")
        return cat == "done"

    async def project_velocity(self, client: httpx.AsyncClient, project_key: str, last_n: int = 6) -> list[dict]:
        boards = await self.project_boards(client, project_key)
        if not boards:
            return []
        board_id = boards[0]["id"]
        sprints = await self.board_sprints(client, board_id, state="closed")
        sprints = sorted(sprints, key=lambda s: s.get("endDate") or "")[-last_n:]
        out = []
        for s in sprints:
            issues = await self.sprint_issues(client, s["id"])
            committed = sum(self._points(i, self.sp_field) for i in issues)
            completed = sum(self._points(i, self.sp_field) for i in issues if self._is_done(i))
            out.append(
                {
                    "sprint": s.get("name"),
                    "committed": round(committed, 1),
                    "completed": round(completed, 1),
                    "end_date": s.get("endDate"),
                }
            )
        return out

    async def project_burndown(self, client: httpx.AsyncClient, project_key: str) -> dict:
        """Current-sprint burndown — remaining points by day."""
        boards = await self.project_boards(client, project_key)
        if not boards:
            return {"sprint": None, "series": []}
        board_id = boards[0]["id"]
        sprints = await self.board_sprints(client, board_id, state="active")
        if not sprints:
            return {"sprint": None, "series": []}
        s = sprints[0]
        issues = await self.sprint_issues(client, s["id"])
        total = sum(self._points(i, self.sp_field) for i in issues)
        # Simple derived series: bucket completed points by resolutiondate.
        completed_by_day: dict[str, float] = defaultdict(float)
        for i in issues:
            if self._is_done(i):
                d = i.get("fields", {}).get("resolutiondate")
                if d:
                    key = d[:10]
                    completed_by_day[key] += self._points(i, self.sp_field)
        series = []
        remaining = total
        for day in sorted(completed_by_day.keys()):
            remaining -= completed_by_day[day]
            series.append({"date": day, "remaining": round(remaining, 1)})
        return {"sprint": s.get("name"), "total": round(total, 1), "series": series}

    async def tickets_per_assignee(self, client: httpx.AsyncClient, project_key: str) -> list[dict]:
        issues = await self.search(
            client,
            f'project = "{project_key}" AND statusCategory != Done',
            ["assignee", "status"],
        )
        agg: dict[str, dict[str, int]] = defaultdict(lambda: {"todo": 0, "in_progress": 0})
        for i in issues:
            name = (i.get("fields", {}).get("assignee") or {}).get("displayName") or "Unassigned"
            cat = i.get("fields", {}).get("status", {}).get("statusCategory", {}).get("key", "")
            bucket = "in_progress" if cat == "indeterminate" else "todo"
            agg[name][bucket] += 1
        return [{"assignee": k, **v} for k, v in sorted(agg.items(), key=lambda x: -(x[1]["todo"] + x[1]["in_progress"]))]

    async def cycle_time(self, client: httpx.AsyncClient, project_key: str, last_n: int = 30) -> list[dict]:
        issues = await self.search(
            client,
            f'project = "{project_key}" AND statusCategory = Done ORDER BY resolutiondate DESC',
            ["created", "resolutiondate", "summary"],
            max_results=last_n,
        )
        out = []
        for i in issues[:last_n]:
            f = i.get("fields", {})
            created = f.get("created")
            resolved = f.get("resolutiondate")
            if not (created and resolved):
                continue
            c = datetime.fromisoformat(created.replace("Z", "+00:00"))
            r = datetime.fromisoformat(resolved.replace("Z", "+00:00"))
            out.append({"key": i["key"], "days": round((r - c).total_seconds() / 86400, 2)})
        return out

    async def issue_type_breakdown(self, client: httpx.AsyncClient, project_key: str) -> list[dict]:
        issues = await self.search(
            client,
            f'project = "{project_key}"',
            ["issuetype"],
        )
        c = Counter(i.get("fields", {}).get("issuetype", {}).get("name", "Unknown") for i in issues)
        return [{"type": k, "count": v} for k, v in c.most_common()]

    # ---------------- Issue creation ----------------

    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str = "",
        issue_type: str = "Story",
        priority: str = "Medium",
        story_points: int | None = None,
        labels: list[str] | None = None,
    ) -> dict:
        """Create a JIRA issue and return the created issue key + id."""
        payload: dict = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
            }
        }
        if description:
            payload["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            }
        if story_points is not None:
            payload["fields"][self.sp_field] = story_points
        if labels:
            payload["fields"]["labels"] = labels

        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self.base}/rest/api/3/issue",
                json=payload,
                auth=self.auth,
                timeout=30,
            )
            r.raise_for_status()
            return r.json()  # {"id": "...", "key": "PRJ0-42", "self": "..."}

    async def throughput(self, client: httpx.AsyncClient, project_key: str, days: int = 30) -> list[dict]:
        issues = await self.search(
            client,
            f'project = "{project_key}" AND resolved >= -{days}d',
            ["resolutiondate"],
        )
        buckets: dict[str, int] = defaultdict(int)
        for i in issues:
            d = i.get("fields", {}).get("resolutiondate")
            if d:
                buckets[d[:10]] += 1
        return [{"date": k, "done": v} for k, v in sorted(buckets.items())]

    async def project_summary(self, client: httpx.AsyncClient, project_key: str) -> dict:
        """Lightweight counts for portfolio card."""
        issues = await self.search(client, f'project = "{project_key}"', ["status"])
        total = len(issues)
        done = sum(1 for i in issues if self._is_done(i))
        in_prog = sum(
            1
            for i in issues
            if i.get("fields", {}).get("status", {}).get("statusCategory", {}).get("key") == "indeterminate"
        )
        todo = total - done - in_prog
        return {
            "key": project_key,
            "total": total,
            "done": done,
            "in_progress": in_prog,
            "todo": todo,
            "completion_pct": round((done / total * 100) if total else 0.0, 1),
        }

    # ---------------- Write operations ----------------

    @staticmethod
    def _build_adf_paragraph(text: str) -> dict:
        """Minimal ADF doc wrapping text in a paragraph node."""
        return {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        }

    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description_adf: dict,
        issue_type: str = "Story",
        priority: str = "Medium",
        story_points: float | None = None,
        labels: list[str] | None = None,
        sprint_id: int | None = None,
    ) -> dict:
        """Create JIRA issue. Returns {key, id, self}."""
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description_adf,
            "issuetype": {"name": issue_type},
            "priority": {"name": priority},
        }
        if story_points is not None:
            fields["customfield_10016"] = story_points
        if labels:
            fields["labels"] = labels
        if sprint_id is not None:
            fields["customfield_10020"] = {"id": sprint_id}

        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self.base}/rest/api/3/issue",
                json={"fields": fields},
                auth=self.auth,
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            return {"key": data["key"], "id": data["id"], "self": data["self"]}

    async def get_transitions(self, issue_key: str) -> list[dict]:
        """GET /rest/api/3/issue/{key}/transitions — returns [{id, name}]."""
        async with httpx.AsyncClient() as c:
            r = await c.get(
                f"{self.base}/rest/api/3/issue/{issue_key}/transitions",
                auth=self.auth,
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            return [{"id": t["id"], "name": t["name"]} for t in data.get("transitions", [])]

    async def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        """POST /rest/api/3/issue/{key}/transitions."""
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self.base}/rest/api/3/issue/{issue_key}/transitions",
                json={"transition": {"id": transition_id}},
                auth=self.auth,
                timeout=30,
            )
            r.raise_for_status()
            return True

    async def add_comment(self, issue_key: str, body_adf: dict) -> dict:
        """POST /rest/api/3/issue/{key}/comment."""
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self.base}/rest/api/3/issue/{issue_key}/comment",
                json={"body": body_adf},
                auth=self.auth,
                timeout=30,
            )
            r.raise_for_status()
            return r.json()

    async def list_transitions_by_name(self, issue_key: str) -> dict[str, str]:
        """Returns {name: id} mapping for easy transition lookup."""
        transitions = await self.get_transitions(issue_key)
        return {t["name"]: t["id"] for t in transitions}

    # ================================================================
    # PM Reporting methods  (used by confluence_reporting.py)
    # ================================================================

    async def project_epics(self, client: httpx.AsyncClient, project_key: str) -> list[dict]:
        """All epics in project with summary, status, priority, assignee, story points."""
        issues = await self.search(
            client,
            f'project = "{project_key}" AND issuetype = Epic ORDER BY priority ASC',
            ["summary", "status", "priority", "assignee", "labels",
             self.sp_field, "duedate", "created", "customfield_10014"],
            max_results=200,
        )
        return [
            {
                "key": i["key"],
                "summary": i["fields"].get("summary", ""),
                "status": i["fields"].get("status", {}).get("name", ""),
                "status_cat": i["fields"].get("status", {}).get("statusCategory", {}).get("key", ""),
                "priority": i["fields"].get("priority", {}).get("name", ""),
                "assignee": (i["fields"].get("assignee") or {}).get("displayName", "Unassigned"),
                "points": self._points(i, self.sp_field),
                "labels": i["fields"].get("labels", []),
                "due": (i["fields"].get("duedate") or "")[:10],
                "created": (i["fields"].get("created") or "")[:10],
            }
            for i in issues
        ]

    async def epic_stories(self, client: httpx.AsyncClient, epic_key: str) -> list[dict]:
        """All stories/tasks under an epic with status, assignee, points."""
        issues = await self.search(
            client,
            f'"Epic Link" = "{epic_key}" OR parent = "{epic_key}" ORDER BY priority ASC',
            ["summary", "status", "priority", "assignee", "issuetype",
             self.sp_field, "subtasks", "resolutiondate"],
            max_results=200,
        )
        return [
            {
                "key": i["key"],
                "summary": i["fields"].get("summary", ""),
                "type": i["fields"].get("issuetype", {}).get("name", ""),
                "status": i["fields"].get("status", {}).get("name", ""),
                "status_cat": i["fields"].get("status", {}).get("statusCategory", {}).get("key", ""),
                "priority": i["fields"].get("priority", {}).get("name", ""),
                "assignee": (i["fields"].get("assignee") or {}).get("displayName", "Unassigned"),
                "points": self._points(i, self.sp_field),
                "subtask_count": len(i["fields"].get("subtasks", [])),
                "resolved": (i["fields"].get("resolutiondate") or "")[:10],
            }
            for i in issues
        ]

    async def project_contributors(self, client: httpx.AsyncClient, project_key: str) -> list[dict]:
        """Unique contributors — all assignees + reporters with their ticket counts."""
        issues = await self.search(
            client,
            f'project = "{project_key}"',
            ["assignee", "reporter", "status"],
            max_results=500,
        )
        contrib: dict[str, dict] = {}
        for i in issues:
            for role, field in [("assignee", "assignee"), ("reporter", "reporter")]:
                person = i["fields"].get(field) or {}
                name = person.get("displayName")
                email = person.get("emailAddress", "")
                if not name:
                    continue
                if name not in contrib:
                    contrib[name] = {"name": name, "email": email, "assigned": 0, "reported": 0, "done": 0}
                contrib[name][role if role == "reporter" else "assigned"] += 1
                if role == "assignee" and self._is_done(i):
                    contrib[name]["done"] += 1
        return sorted(contrib.values(), key=lambda x: -(x["assigned"] + x["reported"]))

    async def current_sprint_details(self, client: httpx.AsyncClient, project_key: str) -> dict:
        """Active sprint with full story list, capacity breakdown, and risk flags."""
        boards = await self.project_boards(client, project_key)
        if not boards:
            return {"sprint": None, "stories": [], "summary": {}}

        board_id = boards[0]["id"]
        sprints = await self.board_sprints(client, board_id, state="active")
        if not sprints:
            return {"sprint": None, "stories": [], "summary": {}}

        sprint = sprints[0]
        issues = await self.sprint_issues(client, sprint["id"])

        total_pts = sum(self._points(i, self.sp_field) for i in issues)
        done_pts = sum(self._points(i, self.sp_field) for i in issues if self._is_done(i))
        in_prog_pts = sum(
            self._points(i, self.sp_field)
            for i in issues
            if i["fields"].get("status", {}).get("statusCategory", {}).get("key") == "indeterminate"
        )
        todo_pts = total_pts - done_pts - in_prog_pts
        pct_done = round((done_pts / total_pts * 100) if total_pts else 0, 1)

        stories = [
            {
                "key": i["key"],
                "summary": i["fields"].get("summary", ""),
                "type": i["fields"].get("issuetype", {}).get("name", ""),
                "status": i["fields"].get("status", {}).get("name", ""),
                "status_cat": i["fields"].get("status", {}).get("statusCategory", {}).get("key", ""),
                "assignee": (i["fields"].get("assignee") or {}).get("displayName", "Unassigned"),
                "points": self._points(i, self.sp_field),
            }
            for i in issues
        ]

        # Assignee capacity view
        cap: dict[str, dict] = {}
        for s in stories:
            a = s["assignee"]
            if a not in cap:
                cap[a] = {"assignee": a, "total_pts": 0, "done_pts": 0, "stories": 0}
            cap[a]["total_pts"] += s["points"]
            cap[a]["stories"] += 1
            if s["status_cat"] == "done":
                cap[a]["done_pts"] += s["points"]

        return {
            "sprint": {
                "name": sprint.get("name"),
                "state": sprint.get("state"),
                "start": (sprint.get("startDate") or "")[:10],
                "end": (sprint.get("endDate") or "")[:10],
                "goal": sprint.get("goal", ""),
            },
            "stories": sorted(stories, key=lambda x: x["assignee"]),
            "summary": {
                "total_pts": round(total_pts, 1),
                "done_pts": round(done_pts, 1),
                "in_progress_pts": round(in_prog_pts, 1),
                "todo_pts": round(todo_pts, 1),
                "pct_done": pct_done,
                "total_stories": len(issues),
            },
            "assignee_capacity": list(cap.values()),
        }

    async def feature_roadmap(self, client: httpx.AsyncClient, project_key: str) -> list[dict]:
        """Build feature roadmap from epics grouped by label or quarter."""
        epics = await self.project_epics(client, project_key)

        # Group by label prefix "feature:" or fall back to epic itself as feature
        features: dict[str, list] = {}
        for e in epics:
            feature_labels = [lb for lb in e["labels"] if lb.lower().startswith("feature:")]
            feature_name = feature_labels[0].split(":", 1)[1].strip() if feature_labels else e["summary"]
            features.setdefault(feature_name, []).append(e)

        roadmap = []
        for feature, epics_list in features.items():
            statuses = [e["status_cat"] for e in epics_list]
            if all(s == "done" for s in statuses):
                overall = "DONE"
            elif any(s == "indeterminate" for s in statuses):
                overall = "IN PROGRESS"
            else:
                overall = "PLANNED"

            total_pts = sum(e["points"] for e in epics_list)
            due_dates = [e["due"] for e in epics_list if e["due"]]
            roadmap.append({
                "feature": feature,
                "epics": epics_list,
                "epic_count": len(epics_list),
                "total_pts": total_pts,
                "status": overall,
                "target_date": max(due_dates) if due_dates else "",
                "assignees": list({e["assignee"] for e in epics_list}),
            })

        return sorted(roadmap, key=lambda x: (x["status"] != "IN PROGRESS", x["target_date"] or "9999"))
