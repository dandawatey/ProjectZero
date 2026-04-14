"""Temporal Knowledge Page Publisher.

Builds and publishes a static Confluence page explaining how Temporal is used
in ProjectZero: architecture, audit trail, governance benefits, workflow stages.

Page title: "ProjectZero — Temporal Workflow Engine"
Published under: CONFLUENCE_PARENT_PAGE_TITLE space root.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CONF_BASE       = os.getenv("CONFLUENCE_BASE_URL", "https://isourceinnovation.atlassian.net/wiki")
CONF_SPACE_KEY  = os.getenv("CONFLUENCE_SPACE_KEY", "PR")
PAGE_TITLE      = "ProjectZero — Temporal Workflow Engine"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _h(n: int, t: str) -> str:
    return f"<h{n}>{t}</h{n}>\n"


def _p(t: str) -> str:
    return f"<p>{t}</p>\n"


def _hr() -> str:
    return "<hr/>\n"


def _panel(ptype: str, title: str, body: str) -> str:
    macro = {"info": "info", "warning": "warning", "success": "success", "note": "note"}.get(ptype, "info")
    return (
        f'<ac:structured-macro ac:name="{macro}">'
        f'<ac:parameter ac:name="title">{title}</ac:parameter>'
        f'<ac:rich-text-body>{body}</ac:rich-text-body>'
        f'</ac:structured-macro>\n'
    )


def _table(headers: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th><strong>{h}</strong></th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>\n"


def _section_header(title: str) -> str:
    return (
        f'<p style="background:#0052CC;color:white;padding:6px 12px;'
        f'border-radius:4px;font-size:14px;font-weight:bold;margin-top:20px;">'
        f'{title}</p>\n'
    )


def _code(lang: str, content: str) -> str:
    return (
        f'<ac:structured-macro ac:name="code">'
        f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
        f'<ac:plain-text-body><![CDATA[{content}]]></ac:plain-text-body>'
        f'</ac:structured-macro>\n'
    )


def build_temporal_page() -> str:
    body = ""

    # ── Masthead ──────────────────────────────────────────────────────────────
    body += (
        f'<p style="background:#091E42;color:white;padding:16px 20px;border-radius:6px;margin-bottom:16px;">'
        f'<span style="font-size:22px;font-weight:bold;">⏱ Temporal Workflow Engine — ProjectZero</span><br/>'
        f'<span style="font-size:13px;opacity:0.85;">Durable execution · Complete audit trail · Governed AI delivery</span><br/>'
        f'<span style="font-size:11px;opacity:0.6;">Last updated: {_now()} · Owner: Yogesh Dandawate (VP AI CoE)</span>'
        f'</p>\n'
    )

    body += _panel(
        "success",
        "What is Temporal?",
        "Temporal is an open-source durable execution platform. Every workflow step is checkpointed to a database. "
        "If a server crashes mid-execution, Temporal replays history and continues exactly where it left off — "
        "no state lost, no manual recovery, complete audit trail of every action ever taken."
    )

    # ── 1. Why Temporal ───────────────────────────────────────────────────────
    body += _section_header("1 · Why ProjectZero Uses Temporal")
    body += _table(
        ["Problem Without Temporal", "Solution With Temporal"],
        [
            ["AI agents run ad-hoc — no record of what happened", "Every activity is an event in Temporal history — permanently recorded"],
            ["Crash mid-workflow = lost work, unknown state", "Temporal replays from last checkpoint — zero data loss"],
            ["No audit trail for governance / ISO 42001", "Full event history: who ran what, when, what it returned"],
            ["Approval gates managed manually in code", "Native signal protocol: workflow pauses, waits for human signal"],
            ["Retry logic hand-coded everywhere", "Built-in retry policy per activity (configurable attempts, backoff)"],
            ["Parallel agent work hard to coordinate", "Child workflows + activity pools — native parallelism"],
            ["Context lost between sessions", "Workflow state persists in Postgres — survives restarts"],
        ]
    )

    # ── 2. Architecture ───────────────────────────────────────────────────────
    body += _section_header("2 · Architecture: How Temporal Fits")
    body += _p(
        "<strong>System flow:</strong> React UI → FastAPI → Postgres → "
        "<strong>Temporal Server</strong> → Temporal Worker → AI Activities (Claude)"
    )
    body += _table(
        ["Component", "Role", "Technology"],
        [
            ["Temporal Server", "Orchestration engine — schedules activities, stores event history", "temporalio/auto-setup Docker or `temporal server start-dev`"],
            ["Temporal Worker", "Executes activities and workflows — runs inside FastAPI process", "Python SDK `temporalio.worker.Worker`"],
            ["Task Queue", "Channel between server and worker — `projectzero-factory`", "Temporal task queue (pull-based)"],
            ["Workflows", "Long-running orchestration logic — Spec→Arch→Impl→Review→Deploy", "`@workflow.defn` classes in Python"],
            ["Activities", "Single units of work — Claude API calls, file writes, DB updates", "`@activity.defn` functions in Python"],
            ["Signals", "Human approval messages sent to running workflow", "`@workflow.signal` handlers"],
            ["Queries", "Read current workflow state without side effects", "`@workflow.query` handlers"],
        ]
    )

    # ── 3. Workflow Stages ────────────────────────────────────────────────────
    body += _section_header("3 · The FeatureDevelopmentWorkflow — Stage by Stage")
    body += _p(
        "Every product feature and every PRJ0 factory ticket runs through the same "
        "governed pipeline. No stage can be skipped. Every stage requires explicit human approval."
    )
    body += _table(
        ["Stage", "Activity", "Agent", "Gate", "Artifact"],
        [
            ["1. Specification", "spec_activity", "Spec Agent (Claude)", "Human approval required → advance to Arch", ".claude/specs/{ticket}-spec.md"],
            ["2. Architecture", "arch_activity", "Arch Agent (Claude)", "Human approval required → advance to Impl", "docs/adr/{ticket}-adr.md"],
            ["3a. Implementation", "impl_activity", "Impl Agent (Claude)", "Auto → flows to Review", ".claude/impl/{ticket}-impl.md"],
            ["3b. Review", "review_activity", "Review Agent (Claude)", "Human approval required → advance to Deploy", ".claude/reviews/{ticket}-review.md"],
            ["4. Deployment", "deploy_activity", "Deploy Agent (Claude)", "Completion — workflow closes", ".claude/releases/{ticket}-release.md"],
        ]
    )

    body += _panel(
        "info",
        "Factory Self-Build (FactorySelfBuildWorkflow)",
        "ProjectZero builds itself using the same pipeline. When a PRJ0 JIRA ticket moves to "
        "<strong>In Progress</strong>, a <code>FactorySelfBuildWorkflow</code> starts automatically "
        "via JIRA webhook → <code>POST /api/v1/factory-build/webhook/jira</code>. "
        "Factory activities are identical in structure but carry factory-specific system prompts "
        "(aware of FastAPI/React/Postgres/Temporal stack, MCRA governance, 80% coverage requirement)."
    )

    # ── 4. Audit Trail ────────────────────────────────────────────────────────
    body += _section_header("4 · Complete Audit Trail — How It Works")
    body += _p(
        "Temporal's event history is immutable. Every action — activity start, activity completion, "
        "signal received, retry attempted — is stored permanently in Temporal's Postgres backend."
    )
    body += _table(
        ["Audit Event", "What Is Recorded", "ISO 42001 Relevance"],
        [
            ["WorkflowExecutionStarted", "Who triggered it, when, input parameters, workflow ID", "A.8.1 — AI system lifecycle traceability"],
            ["ActivityTaskScheduled", "Which activity (spec/arch/impl/review/deploy), timestamp", "A.8.3 — Human oversight of AI actions"],
            ["ActivityTaskStarted", "Worker that picked it up, attempt number", "A.9.3 — Performance monitoring"],
            ["ActivityTaskCompleted", "Output payload — artifact path, summary, status", "A.10.2 — Incident and output tracking"],
            ["ActivityTaskFailed", "Error message, stack trace, attempt count", "A.10.1 — Nonconformity and corrective action"],
            ["SignalReceived (approve_stage)", "Stage approved/rejected, comment, timestamp", "A.6.1 — Human-in-the-loop evidence"],
            ["WorkflowExecutionCompleted", "Final status (completed/failed), all stage results", "A.9.1 — Evidence of completed AI action"],
            ["WorkflowExecutionTimedOut", "Stage that timed out, duration", "A.10.2 — Incident register trigger"],
        ]
    )

    body += _panel(
        "success",
        "ISO 42001 Evidence — Automatic",
        "Every Temporal event history entry is timestamped, immutable, and queryable via Temporal UI "
        "or the Temporal SDK. Auditors can replay the exact sequence of AI actions for any feature, "
        "see every human approval, every rejection, every retry. No manual logging required."
    )

    # ── 5. Approval Gates ─────────────────────────────────────────────────────
    body += _section_header("5 · Human Approval Gates (MCRA Protocol)")
    body += _p(
        "After each major stage (Spec, Arch, Realization), the workflow pauses and waits for an explicit "
        "human approval signal. This implements the <strong>Maker → Checker → Reviewer → Approver</strong> "
        "4-eye governance model natively in Temporal."
    )
    body += _code("bash", """\
# Approve specification stage → workflow advances to architecture
curl -X POST http://localhost:8000/api/v1/commands/approve \\
  -H "Content-Type: application/json" \\
  -d '{
    "workflow_run_id": "<uuid>",
    "stage": "specification",
    "approved": true,
    "comment": "Acceptance criteria complete, stories well-defined"
  }'

# Reject → workflow signals failure, maker is notified
curl -X POST http://localhost:8000/api/v1/commands/approve \\
  -d '{"workflow_run_id": "<uuid>", "stage": "specification", "approved": false,
       "comment": "Missing non-functional requirements"}'""")

    body += _table(
        ["Signal", "Effect", "Timeout"],
        [
            ["approve_stage (approved=true)", "Workflow unblocks → next stage activity starts", "7 days — then workflow times out and alerts"],
            ["approve_stage (approved=false)", "Workflow raises CancelledError → status=failed in DB", "N/A"],
        ]
    )

    # ── 6. Factory Self-Build ─────────────────────────────────────────────────
    body += _section_header("6 · Factory Self-Build — ProjectZero Builds Itself")
    body += _p(
        "ProjectZero does not get special treatment. PRJ0 tickets go through the same "
        "Temporal governance pipeline. This ensures the factory's own codebase is "
        "built with the same rigor, auditability, and MCRA gates it enforces on all products."
    )
    body += _table(
        ["Trigger", "Action"],
        [
            ["PRJ0 ticket → In Progress (JIRA webhook)", "FactorySelfBuildWorkflow starts automatically"],
            ["Manual trigger via API", "POST /api/v1/factory-build with {jira_ticket_id: 'PRJ0-XX'}"],
            ["Approval via Control Tower UI", "POST /api/v1/commands/approve with workflow_run_id"],
        ]
    )
    body += _code("bash", """\
# Manually start factory self-build for a PRJ0 ticket
curl -X POST http://localhost:8000/api/v1/factory-build \\
  -H "Content-Type: application/json" \\
  -d '{"jira_ticket_id": "PRJ0-55"}'

# JIRA webhook URL to configure in JIRA project settings:
# https://your-api-host/api/v1/factory-build/webhook/jira
# Events: Issue Updated (filter: project=PRJ0, status=In Progress)""")

    # ── 7. Benefits ───────────────────────────────────────────────────────────
    body += _section_header("7 · Benefits Summary")
    body += _table(
        ["Benefit", "Detail", "Stakeholder"],
        [
            ["Zero data loss", "Temporal checkpoints every step — crash recovery is automatic", "Engineering"],
            ["Complete audit trail", "Immutable event history for every AI action, every approval", "Compliance / ISO 42001"],
            ["Governance enforcement", "Stages cannot be skipped — approval gates are code, not process", "Governance / CTO"],
            ["Retry resilience", "Claude API failures auto-retry (3× with backoff) — no manual intervention", "Engineering"],
            ["Human oversight evidence", "Every approve_stage signal is timestamped and stored — ISO A.8.3 proof", "Compliance"],
            ["Observability", "Temporal UI shows real-time workflow state, history, failures", "Engineering / PM"],
            ["Scalability", "Multiple workers on same task queue — parallel feature builds", "Engineering"],
            ["Self-governing factory", "PRJ0 tickets go through same pipeline — factory eats its own dog food", "CTO / Governance"],
        ]
    )

    # ── 8. Monitoring ─────────────────────────────────────────────────────────
    body += _section_header("8 · Monitoring & Operations")
    body += _table(
        ["Tool", "URL", "Purpose"],
        [
            ["Temporal UI", "http://localhost:8233", "View workflows, event history, replay, search"],
            ["Factory API Docs", "http://localhost:8000/docs", "REST API for workflow triggers and approvals"],
            ["Factory Dashboard", "http://localhost:3000", "React Control Tower — workflow status, approvals"],
            ["Temporal Status API", "GET /api/v1/temporal/status", "Health check for Temporal connection"],
            ["Agent Map API", "GET /api/v1/commands/agent-map", "Stage → agent mapping for all workflows"],
        ]
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    body += _hr()
    body += (
        f'<p style="font-size:11px;color:#6B778C;">'
        f'Auto-generated by ProjectZeroFactory · {_now()} · '
        f'Owner: Yogesh Dandawate (VP AI CoE) · '
        f'Temporal docs: <a href="https://docs.temporal.io">docs.temporal.io</a>'
        f'</p>\n'
    )

    return body


async def publish_temporal_page() -> dict[str, Any]:
    """Publish the Temporal knowledge page to Confluence."""
    conf_base = CONF_BASE.rstrip("/")
    email     = os.getenv("JIRA_USER_EMAIL", "")
    token     = os.getenv("CONFLUENCE_API_TOKEN", "") or os.getenv("JIRA_API_TOKEN", "")

    if not all([conf_base, email, token]):
        return {"status": "error", "detail": "Confluence credentials not configured"}

    auth = (email, token)
    body_html = build_temporal_page()
    parent_title = os.getenv("CONFLUENCE_PARENT_PAGE_TITLE", "ProjectZero Products")

    async with httpx.AsyncClient() as c:
        # Find or create parent
        r = await c.get(
            f"{conf_base}/rest/api/content",
            params={"spaceKey": CONF_SPACE_KEY, "title": parent_title, "expand": "version"},
            auth=auth, timeout=15,
        )
        results = r.json().get("results", [])
        parent_id = results[0]["id"] if results else None

        # Check if page already exists
        r2 = await c.get(
            f"{conf_base}/rest/api/content",
            params={"spaceKey": CONF_SPACE_KEY, "title": PAGE_TITLE, "expand": "version"},
            auth=auth, timeout=15,
        )
        existing = r2.json().get("results", [])

        if existing:
            page_id = existing[0]["id"]
            version = existing[0]["version"]["number"]
            payload = {
                "type": "page", "title": PAGE_TITLE,
                "version": {"number": version + 1},
                "body": {"storage": {"value": body_html, "representation": "storage"}},
            }
            await c.put(f"{conf_base}/rest/api/content/{page_id}",
                        json=payload, auth=auth,
                        headers={"Content-Type": "application/json"}, timeout=30)
        else:
            payload = {
                "type": "page", "title": PAGE_TITLE,
                "space": {"key": CONF_SPACE_KEY},
                "body": {"storage": {"value": body_html, "representation": "storage"}},
            }
            if parent_id:
                payload["ancestors"] = [{"id": parent_id}]
            r3 = await c.post(f"{conf_base}/rest/api/content",
                              json=payload, auth=auth,
                              headers={"Content-Type": "application/json"}, timeout=30)
            page_id = r3.json().get("id")

        # Set full-width
        for prop_key in ("content-appearance-published", "content-appearance-draft"):
            try:
                rp = await c.get(f"{conf_base}/rest/api/content/{page_id}/property/{prop_key}",
                                 auth=auth, timeout=10)
                if rp.status_code == 200:
                    pv = rp.json().get("version", {}).get("number", 1)
                    await c.put(
                        f"{conf_base}/rest/api/content/{page_id}/property/{prop_key}",
                        json={"key": prop_key, "value": "full-width", "version": {"number": pv + 1}},
                        auth=auth, headers={"Content-Type": "application/json"}, timeout=10,
                    )
                else:
                    await c.post(
                        f"{conf_base}/rest/api/content/{page_id}/property",
                        json={"key": prop_key, "value": "full-width"},
                        auth=auth, headers={"Content-Type": "application/json"}, timeout=10,
                    )
            except Exception:
                pass

        page_url = f"{conf_base}/spaces/{CONF_SPACE_KEY}/pages/{page_id}"
        logger.info("Temporal knowledge page published → %s", page_url)
        return {"status": "published", "page_id": page_id, "url": page_url, "title": PAGE_TITLE}
