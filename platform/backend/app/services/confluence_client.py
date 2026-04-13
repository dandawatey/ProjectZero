"""Confluence REST API client.

Manages per-product page hierarchies and keeps them in sync with workflow
state, artifacts, decisions, and architecture docs.

Page structure per product:
  {confluence_parent_page_title}
  └── {ProductName}                ← product root (auto-created)
      ├── Overview                 ← PRD / BMAD summary
      ├── Architecture             ← ADRs, tech stack, DB schema, API contracts
      ├── Workflow History         ← stage progress, current status, blockers
      ├── Artifacts                ← links to generated artifacts
      └── Decisions                ← Brain decisions record
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def _base() -> str:
    return os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")


def _auth() -> tuple[str, str]:
    email = os.getenv("JIRA_USER_EMAIL", "")
    token = os.getenv("CONFLUENCE_API_TOKEN", "") or os.getenv("JIRA_API_TOKEN", "")
    return (email, token)


def _space_key() -> str:
    return os.getenv("CONFLUENCE_SPACE_KEY", "PZF")


def _configured() -> bool:
    base, (email, token) = _base(), _auth()
    return bool(base and email and token)


# ---------------------------------------------------------------------------
# HTML page body helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _section(title: str, body: str) -> str:
    return f"<h2>{title}</h2>\n{body}\n"


def _kv_table(rows: list[tuple[str, str]]) -> str:
    cells = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    return f"<table><tbody>{cells}</tbody></table>"


def _status_badge(status: str) -> str:
    colors = {
        "running": "#0052CC",
        "completed": "#00875A",
        "failed": "#DE350B",
        "pending": "#FF8B00",
        "blocked": "#FF8B00",
    }
    color = colors.get(status.lower(), "#6B778C")
    return (
        f'<ac:structured-macro ac:name="status">'
        f'<ac:parameter ac:name="colour">{color}</ac:parameter>'
        f'<ac:parameter ac:name="title">{status.upper()}</ac:parameter>'
        f'</ac:structured-macro>'
    )


def build_overview_body(product_name: str, prd: dict | None, bmad: dict | None) -> str:
    rows = [("Product", product_name), ("Last Updated", _now())]
    if prd:
        rows += [
            ("Vision", prd.get("vision", "—")),
            ("Problem", prd.get("problem", "—")),
            ("Target Users", prd.get("target_users", "—")),
            ("Success Metrics", prd.get("success_metrics", "—")),
        ]
    if bmad:
        rows += [
            ("Business", bmad.get("business", "—")),
            ("Market", bmad.get("market", "—")),
            ("Architecture", bmad.get("architecture", "—")),
            ("Delivery", bmad.get("delivery", "—")),
        ]
    body = _section("Product Overview", _kv_table(rows))
    if prd and prd.get("features"):
        items = "".join(f"<li>{f}</li>" for f in prd["features"])
        body += _section("Features", f"<ul>{items}</ul>")
    return body


def build_architecture_body(adrs: list[dict], tech_stack: dict | None, api_notes: str | None) -> str:
    body = _section("Architecture", f"<p>Last updated: {_now()}</p>")
    if tech_stack:
        rows = [(k, v) for k, v in tech_stack.items()]
        body += _section("Tech Stack", _kv_table(rows))
    if adrs:
        adr_rows = [(a.get("title", ""), a.get("decision", "")) for a in adrs]
        body += _section("Architecture Decision Records", _kv_table(adr_rows))
    if api_notes:
        body += _section("API Contracts", f"<pre>{api_notes}</pre>")
    return body


def build_workflow_history_body(workflows: list[dict]) -> str:
    if not workflows:
        return "<p>No workflows recorded yet.</p>"
    rows: list[tuple[str, str]] = []
    for w in workflows:
        status_cell = _status_badge(w.get("status", "unknown"))
        rows.append((
            w.get("workflow_type", "unknown"),
            f"{status_cell} — Stage: {w.get('current_stage', '—')} | "
            f"Started: {w.get('created_at', '—')}",
        ))
    return _section("Workflow History", _kv_table(rows))


def build_artifacts_body(artifacts: list[dict]) -> str:
    if not artifacts:
        return "<p>No artifacts generated yet.</p>"
    rows = [(a.get("artifact_type", ""), a.get("content_path", "")) for a in artifacts]
    return _section("Generated Artifacts", _kv_table(rows))


def build_decisions_body(decisions: list[dict]) -> str:
    if not decisions:
        return "<p>No decisions recorded yet.</p>"
    parts = []
    for d in decisions:
        parts.append(
            f"<h3>{d.get('title', 'Untitled')}</h3>"
            f"<p><strong>Context:</strong> {d.get('context', '—')}</p>"
            f"<p><strong>Decision:</strong> {d.get('chosen', '—')}</p>"
            f"<p><strong>Rationale:</strong> {d.get('rationale', '—')}</p>"
            f"<p><strong>Status:</strong> {d.get('status', '—')}</p>"
            f"<hr/>"
        )
    return _section("Architecture & Product Decisions", "".join(parts))


# ---------------------------------------------------------------------------
# ConfluenceClient
# ---------------------------------------------------------------------------

class ConfluenceClient:
    """Async Confluence REST v2 client."""

    def __init__(self) -> None:
        if not _configured():
            raise RuntimeError("Confluence credentials not configured")
        self.base = _base()
        self.auth = _auth()
        self.space_key = _space_key()

    # ------------------------------------------------------------------
    # Low-level HTTP helpers
    # ------------------------------------------------------------------

    async def _get(self, client: httpx.AsyncClient, path: str, params: dict | None = None) -> dict:
        r = await client.get(f"{self.base}{path}", params=params, auth=self.auth, timeout=30)
        r.raise_for_status()
        return r.json()

    async def _post(self, client: httpx.AsyncClient, path: str, payload: dict) -> dict:
        r = await client.post(
            f"{self.base}{path}",
            json=payload,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    async def _put(self, client: httpx.AsyncClient, path: str, payload: dict) -> dict:
        r = await client.put(
            f"{self.base}{path}",
            json=payload,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # Space & page lookup
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as c:
                await self._get(c, "/rest/api/space", {"limit": 1})
            return True
        except Exception as exc:
            logger.warning("Confluence health check failed: %s", exc)
            return False

    async def find_page(self, title: str, space_key: str | None = None) -> dict | None:
        """Return page dict if found, else None."""
        sk = space_key or self.space_key
        try:
            async with httpx.AsyncClient() as c:
                data = await self._get(
                    c,
                    "/rest/api/content",
                    {"spaceKey": sk, "title": title, "expand": "version,body.storage"},
                )
            results = data.get("results", [])
            return results[0] if results else None
        except Exception as exc:
            logger.error("find_page(%s) failed: %s", title, exc)
            return None

    async def get_or_create_parent_page(self, parent_title: str) -> str | None:
        """Return page ID of parent, creating it if absent."""
        page = await self.find_page(parent_title)
        if page:
            return page["id"]
        # Create root parent page
        return await self._create_page(
            title=parent_title,
            body=f"<p>ProjectZero Factory — product space. Auto-created {_now()}.</p>",
            parent_id=None,
        )

    # ------------------------------------------------------------------
    # Page CRUD
    # ------------------------------------------------------------------

    async def _create_page(self, title: str, body: str, parent_id: str | None) -> str | None:
        payload: dict[str, Any] = {
            "type": "page",
            "title": title,
            "space": {"key": self.space_key},
            "body": {"storage": {"value": body, "representation": "storage"}},
        }
        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]
        try:
            async with httpx.AsyncClient() as c:
                result = await self._post(c, "/rest/api/content", payload)
            page_id = result.get("id")
            logger.info("Created Confluence page '%s' id=%s", title, page_id)
            return page_id
        except Exception as exc:
            logger.error("_create_page(%s) failed: %s", title, exc)
            return None

    async def _update_page(self, page_id: str, title: str, body: str, current_version: int) -> bool:
        payload = {
            "type": "page",
            "title": title,
            "version": {"number": current_version + 1},
            "body": {"storage": {"value": body, "representation": "storage"}},
        }
        try:
            async with httpx.AsyncClient() as c:
                await self._put(c, f"/rest/api/content/{page_id}", payload)
            logger.info("Updated Confluence page id=%s version=%d", page_id, current_version + 1)
            return True
        except Exception as exc:
            logger.error("_update_page(%s) failed: %s", page_id, exc)
            return False

    async def upsert_page(self, title: str, body: str, parent_id: str | None) -> str | None:
        """Create page if absent, otherwise update it. Returns page ID."""
        existing = await self.find_page(title)
        if existing:
            version = existing.get("version", {}).get("number", 1)
            await self._update_page(existing["id"], title, body, version)
            return existing["id"]
        return await self._create_page(title, body, parent_id)

    # ------------------------------------------------------------------
    # Per-product page hierarchy
    # ------------------------------------------------------------------

    async def ensure_product_pages(self, product_name: str, parent_title: str) -> dict[str, str | None]:
        """
        Ensure full page hierarchy exists for a product.
        Returns dict of {section: page_id}.
        """
        if not _configured():
            return {}

        parent_id = await self.get_or_create_parent_page(parent_title)

        # Product root page
        root_id = await self.upsert_page(
            title=product_name,
            body=f"<p>Product workspace for <strong>{product_name}</strong>. Auto-managed by ProjectZeroFactory.</p>",
            parent_id=parent_id,
        )

        sections = ["Overview", "Architecture", "Workflow History", "Artifacts", "Decisions"]
        page_ids: dict[str, str | None] = {"root": root_id}
        for section in sections:
            pid = await self.upsert_page(
                title=f"{product_name} — {section}",
                body=f"<p>Auto-managed by ProjectZeroFactory. Last sync: {_now()}</p>",
                parent_id=root_id,
            )
            page_ids[section.lower().replace(" ", "_")] = pid

        return page_ids

    async def sync_overview(self, product_name: str, prd: dict | None, bmad: dict | None) -> bool:
        existing = await self.find_page(f"{product_name} — Overview")
        if not existing:
            logger.warning("Overview page for %s not found — run ensure_product_pages first", product_name)
            return False
        body = build_overview_body(product_name, prd, bmad)
        version = existing.get("version", {}).get("number", 1)
        return await self._update_page(existing["id"], f"{product_name} — Overview", body, version)

    async def sync_architecture(
        self, product_name: str, adrs: list[dict], tech_stack: dict | None = None, api_notes: str | None = None
    ) -> bool:
        existing = await self.find_page(f"{product_name} — Architecture")
        if not existing:
            return False
        body = build_architecture_body(adrs, tech_stack, api_notes)
        version = existing.get("version", {}).get("number", 1)
        return await self._update_page(existing["id"], f"{product_name} — Architecture", body, version)

    async def sync_workflow_history(self, product_name: str, workflows: list[dict]) -> bool:
        existing = await self.find_page(f"{product_name} — Workflow History")
        if not existing:
            return False
        body = build_workflow_history_body(workflows)
        version = existing.get("version", {}).get("number", 1)
        return await self._update_page(existing["id"], f"{product_name} — Workflow History", body, version)

    async def sync_artifacts(self, product_name: str, artifacts: list[dict]) -> bool:
        existing = await self.find_page(f"{product_name} — Artifacts")
        if not existing:
            return False
        body = build_artifacts_body(artifacts)
        version = existing.get("version", {}).get("number", 1)
        return await self._update_page(existing["id"], f"{product_name} — Artifacts", body, version)

    async def sync_decisions(self, product_name: str, decisions: list[dict]) -> bool:
        existing = await self.find_page(f"{product_name} — Decisions")
        if not existing:
            return False
        body = build_decisions_body(decisions)
        version = existing.get("version", {}).get("number", 1)
        return await self._update_page(existing["id"], f"{product_name} — Decisions", body, version)

    # ------------------------------------------------------------------
    # CXO Dashboard pages (PRJ0-41)
    # ------------------------------------------------------------------

    async def publish_cxo_portfolio(self, projects: list[dict], parent_title: str) -> str | None:
        """Publish/update a CXO Portfolio overview page in Confluence."""
        parent_id = await self.get_or_create_parent_page(parent_title)
        body = self._build_cxo_portfolio_body(projects)
        return await self.upsert_page(
            title="CXO Portfolio Dashboard",
            body=body,
            parent_id=parent_id,
        )

    async def publish_cxo_project(self, project_key: str, metrics: dict, parent_title: str) -> str | None:
        """Publish/update a per-project CXO metrics page in Confluence."""
        # Ensure portfolio parent exists
        parent_id = await self.get_or_create_parent_page(parent_title)
        portfolio_id = await self.upsert_page(
            title="CXO Portfolio Dashboard",
            body=f"<p>CXO Portfolio Dashboard — auto-managed by ProjectZeroFactory. Last sync: {_now()}</p>",
            parent_id=parent_id,
        )
        body = self._build_cxo_project_body(project_key, metrics)
        return await self.upsert_page(
            title=f"CXO — {project_key}",
            body=body,
            parent_id=portfolio_id,
        )

    @staticmethod
    def _build_cxo_portfolio_body(projects: list[dict]) -> str:
        rows = [("Project", "Total", "Done", "In Progress", "Todo", "Completion")]
        for p in projects:
            total = p.get("total", 0) or 0
            done = p.get("done", 0) or 0
            pct = f"{round(done / total * 100)}%" if total else "—"
            rows.append((
                f"<strong>{p.get('key', '—')}</strong> {p.get('name', '')}",
                str(total),
                str(done),
                str(p.get("in_progress", 0) or 0),
                str(p.get("todo", 0) or 0),
                pct,
            ))
        header = "".join(f"<th>{h}</th>" for h in rows[0])
        data_rows = "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
            for row in rows[1:]
        )
        table = f"<table><thead><tr>{header}</tr></thead><tbody>{data_rows}</tbody></table>"
        body = f"<h1>CXO Portfolio Dashboard</h1><p>Last updated: {_now()}</p>\n"
        body += _section("Portfolio Summary", table)
        return body

    @staticmethod
    def _build_cxo_project_body(project_key: str, metrics: dict) -> str:
        summary = metrics.get("summary", {}) or {}
        velocity = metrics.get("velocity", []) or []
        burndown = metrics.get("burndown", {}) or {}
        assignees = metrics.get("assignees", []) or []
        cycle_time = metrics.get("cycle_time", []) or []
        issue_types = metrics.get("issue_types", []) or []
        throughput = metrics.get("throughput", []) or []

        body = f"<h1>{project_key} — Agile Metrics</h1><p>Last updated: {_now()}</p>\n"

        # Summary KPIs
        kpis = [
            ("Project", summary.get("name", project_key)),
            ("Total Tickets", str(summary.get("total", 0))),
            ("Done", str(summary.get("done", 0))),
            ("In Progress", str(summary.get("in_progress", 0))),
            ("Todo", str(summary.get("todo", 0))),
        ]
        body += _section("Key Metrics", _kv_table(kpis))

        # Velocity table
        if velocity:
            vh = "<th>Sprint</th><th>Committed</th><th>Completed</th>"
            vr = "".join(
                f"<tr><td>{v.get('sprint','')}</td><td>{v.get('committed',0)}</td><td>{v.get('completed',0)}</td></tr>"
                for v in velocity
            )
            body += _section("Velocity (last 6 sprints)", f"<table><thead><tr>{vh}</tr></thead><tbody>{vr}</tbody></table>")

        # Burndown
        bd_sprint = (burndown.get("sprint") or {})
        if bd_sprint:
            body += _section("Current Sprint Burndown", _kv_table([
                ("Sprint", bd_sprint.get("name", "—")),
                ("Total Points", str(burndown.get("total", 0))),
            ]))

        # Tickets per assignee
        if assignees:
            ah = "<th>Assignee</th><th>Todo</th><th>In Progress</th><th>Done</th>"
            ar = "".join(
                f"<tr><td>{a.get('assignee','Unassigned')}</td><td>{a.get('todo',0)}</td>"
                f"<td>{a.get('in_progress',0)}</td><td>{a.get('done',0)}</td></tr>"
                for a in assignees
            )
            body += _section("Tickets per Assignee", f"<table><thead><tr>{ah}</tr></thead><tbody>{ar}</tbody></table>")

        # Issue type breakdown
        if issue_types:
            it_rows = [(i.get("issue_type", ""), str(i.get("count", 0))) for i in issue_types]
            body += _section("Issue Type Breakdown", _kv_table(it_rows))

        # Cycle time sample
        if cycle_time:
            ct_rows = [(c.get("key", ""), f"{c.get('cycle_days', 0):.1f} days") for c in cycle_time[:10]]
            body += _section("Cycle Time (sample, days)", _kv_table(ct_rows))

        # Throughput
        if throughput:
            th_h = "<th>Week</th><th>Completed</th>"
            th_r = "".join(
                f"<tr><td>{t.get('week','')}</td><td>{t.get('completed',0)}</td></tr>"
                for t in throughput
            )
            body += _section("Weekly Throughput", f"<table><thead><tr>{th_h}</tr></thead><tbody>{th_r}</tbody></table>")

        return body

    async def sync_all(
        self,
        product_name: str,
        parent_title: str,
        prd: dict | None = None,
        bmad: dict | None = None,
        adrs: list[dict] | None = None,
        tech_stack: dict | None = None,
        workflows: list[dict] | None = None,
        artifacts: list[dict] | None = None,
        decisions: list[dict] | None = None,
    ) -> dict[str, bool]:
        """Full sync of all product sections. Creates pages if missing."""
        await self.ensure_product_pages(product_name, parent_title)
        results = {
            "overview": await self.sync_overview(product_name, prd, bmad),
            "architecture": await self.sync_architecture(product_name, adrs or [], tech_stack),
            "workflow_history": await self.sync_workflow_history(product_name, workflows or []),
            "artifacts": await self.sync_artifacts(product_name, artifacts or []),
            "decisions": await self.sync_decisions(product_name, decisions or []),
        }
        return results

    # ------------------------------------------------------------------
    # ISO/IEC 42001 Audit Report publishing
    # ------------------------------------------------------------------

    async def publish_iso_audit_report(
        self,
        report: dict,
        parent_title: str,
        product_id: str | None = None,
    ) -> str | None:
        """Publish a full ISO 42001 audit readiness report to Confluence.

        Creates/updates under parent_title:
          ISO 42001 Audit Reports
          └── ISO 42001 — {product_id or 'Factory-Wide'} — {date}
        """
        parent_id = await self.get_or_create_parent_page(parent_title)

        # Ensure "ISO 42001 Audit Reports" section exists
        iso_section_id = await self.upsert_page(
            title="ISO 42001 Audit Reports",
            body=f"<p>ISO/IEC 42001:2023 AI Management System audit reports. Auto-generated by ProjectZeroFactory.</p>",
            parent_id=parent_id,
        )

        scope = product_id or "Factory-Wide"
        date_str = _now()[:10]
        page_title = f"ISO 42001 — {scope} — {date_str}"

        body = self._build_iso_report_body(report)
        return await self.upsert_page(title=page_title, body=body, parent_id=iso_section_id)

    @staticmethod
    def _build_iso_report_body(report: dict) -> str:
        summary = report.get("executive_summary", {})
        controls_stats = summary.get("controls", {})
        soa = report.get("statement_of_applicability", [])
        transparency = report.get("transparency_metrics", {})
        risk_summary = report.get("risk_register_summary", {})
        incidents = report.get("incident_summary", {})
        gaps = report.get("gap_remediation_backlog", [])

        readiness = summary.get("audit_readiness", "—")
        compliance_pct = summary.get("overall_compliance_pct", 0)

        # Readiness banner colour
        if "GREEN" in readiness:
            banner_color = "#00875A"
        elif "AMBER" in readiness:
            banner_color = "#FF8B00"
        else:
            banner_color = "#DE350B"

        body = f"""
<h1>ISO/IEC 42001:2023 — AI Management System Audit Report</h1>
<p>Generated: {_now()}</p>
<p><strong>Audit Readiness:</strong>
  <span style="background:{banner_color};color:white;padding:4px 10px;border-radius:4px;font-weight:bold;">
    {readiness}
  </span>
</p>
"""

        # Executive Summary
        exec_rows = [
            ("Overall Compliance", f"{compliance_pct}%"),
            ("Total Controls", str(controls_stats.get("total", 0))),
            ("Compliant", str(controls_stats.get("compliant", 0))),
            ("Partial", str(controls_stats.get("partial", 0))),
            ("Non-Compliant", str(controls_stats.get("non_compliant", 0))),
            ("Not Assessed", str(controls_stats.get("not_assessed", 0))),
            ("Open Critical Incidents", str(summary.get("open_critical_incidents", 0))),
            ("Pending Human Reviews", str(summary.get("pending_human_reviews", 0))),
            ("AI Outcome Acceptance Rate", f"{summary.get('ai_outcome_acceptance_rate_pct', 0)}%"),
        ]
        body += _section("Executive Summary", _kv_table(exec_rows))

        # Statement of Applicability
        if soa:
            STATUS_COLORS = {
                "COMPLIANT": "#00875A",
                "PARTIAL": "#FF8B00",
                "NON_COMPLIANT": "#DE350B",
                "not_assessed": "#6B778C",
                "NOT_APPLICABLE": "#97A0AF",
            }
            soa_header = "<th>Control</th><th>Name</th><th>Category</th><th>Status</th><th>Score</th><th>Owner</th>"
            soa_rows = ""
            for c in soa:
                color = STATUS_COLORS.get(c.get("status", ""), "#6B778C")
                status_badge = (
                    f'<span style="background:{color};color:white;padding:2px 6px;'
                    f'border-radius:3px;font-size:11px;">{c.get("status","—")}</span>'
                )
                soa_rows += (
                    f"<tr>"
                    f"<td><strong>{c.get('control_id','')}</strong></td>"
                    f"<td>{c.get('control_name','')}</td>"
                    f"<td>{c.get('category','')}</td>"
                    f"<td>{status_badge}</td>"
                    f"<td>{c.get('score','—')}</td>"
                    f"<td>{c.get('remediation_owner','—')}</td>"
                    f"</tr>"
                )
            body += _section(
                "Statement of Applicability (Annex A)",
                f"<table><thead><tr>{soa_header}</tr></thead><tbody>{soa_rows}</tbody></table>",
            )

        # Risk Register Summary
        risk_by_level = risk_summary.get("by_level", {})
        if risk_by_level:
            risk_rows = [(level, str(count)) for level, count in risk_by_level.items()]
            body += _section("AI Risk Register Summary", _kv_table(risk_rows))

        high_risk = risk_summary.get("high_risk_items", [])
        if high_risk:
            hr_header = "<th>Use Case</th><th>Risk Level</th><th>Oversight</th><th>Owner</th><th>Model</th>"
            hr_rows = "".join(
                f"<tr><td>{r.get('use_case','')}</td><td>{r.get('risk_level','')}</td>"
                f"<td>{r.get('oversight','')}</td><td>{r.get('owner','—')}</td>"
                f"<td>{r.get('model','—')}</td></tr>"
                for r in high_risk
            )
            body += _section(
                "High / Prohibited Risk AI Uses",
                f"<table><thead><tr>{hr_header}</tr></thead><tbody>{hr_rows}</tbody></table>",
            )

        # Transparency Metrics
        t_rows = [
            ("Total AI Actions", str(transparency.get("total_ai_actions", 0))),
            ("Requiring Human Review", str(transparency.get("requiring_human_review", 0))),
            ("Reviews Completed", str(transparency.get("human_reviews_completed", 0))),
            ("Review Completion", f"{transparency.get('review_completion_pct', 0)}%"),
            ("Outcomes Accepted", str(transparency.get("outcomes_accepted", 0))),
            ("Outcomes Rejected", str(transparency.get("outcomes_rejected", 0))),
            ("Acceptance Rate", f"{transparency.get('acceptance_rate_pct', 0)}%"),
        ]
        body += _section("AI Transparency & Human Oversight Metrics (A.8.3 / A.9.3)", _kv_table(t_rows))

        # Incident Summary
        inc_rows = [
            ("Total Incidents", str(incidents.get("total", 0))),
            ("Open Critical", str(incidents.get("open_critical", 0))),
        ]
        body += _section("AI Incident Register Summary (A.10.2)", _kv_table(inc_rows))

        # Gap Backlog
        if gaps:
            gap_header = "<th>Control</th><th>Name</th><th>Status</th><th>Risk</th><th>Owner</th><th>Due</th>"
            gap_rows = "".join(
                f"<tr><td>{g.get('control_id','')}</td><td>{g.get('control_name','')}</td>"
                f"<td>{g.get('status','')}</td><td>{g.get('risk','—')}</td>"
                f"<td>{g.get('owner','—')}</td><td>{g.get('due','—')}</td></tr>"
                for g in gaps
            )
            body += _section(
                "Gap Remediation Backlog",
                f"<table><thead><tr>{gap_header}</tr></thead><tbody>{gap_rows}</tbody></table>",
            )
        else:
            body += _section("Gap Remediation Backlog", "<p>No open gaps.</p>")

        return body
