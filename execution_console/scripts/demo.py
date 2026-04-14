#!/usr/bin/env python3
"""Demo mode — inject mock events and show Rich console — PRJ0-56."""
import sys, time, random, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.events import ExecutionEvent, ExecStatus
from app.services.event_store import init_db, store_event, clear_all
from app.services.state_engine import build_snapshot
from app.renderers.rich_console import run_live_console

DEMO_TICKETS = [
    ("PRJ0-49", "EPIC-AGENT", "feature:agents", "impl-agent", "impl_activity"),
    ("PRJ0-50", "EPIC-AGENT", "feature:agents", "spec-agent", "spec_activity"),
    ("PRJ0-51", "EPIC-AGENT", "feature:agents", "arch-agent", "arch_activity"),
    ("PRJ0-34", "EPIC-GOV",   "feature:governance", "review-agent", "review_activity"),
    ("PRJ0-37", "EPIC-GOV",   "feature:governance", "impl-agent", "impl_activity"),
    ("PRJ0-22", "EPIC-UI",    "feature:ui", "deploy-agent", "deploy_activity"),
]

def inject_demo_events():
    """Inject a stream of mock events simulating a real run."""
    init_db()
    clear_all()

    jira_base = "https://isourceinnovation.atlassian.net/browse"

    for i, (ticket, epic, feature, agent, step) in enumerate(DEMO_TICKETS):
        status = random.choice([
            ExecStatus.RUNNING, ExecStatus.RUNNING, ExecStatus.SUCCESS,
            ExecStatus.QUEUED, ExecStatus.FAILED,
        ])
        pct = 100.0 if status == ExecStatus.SUCCESS else (
            0.0 if status == ExecStatus.QUEUED else random.uniform(10, 90)
        )
        store_event(ExecutionEvent(
            event_type="ticket_status",
            feature_id=feature,
            epic_key=epic,
            ticket_id=ticket,
            workflow_run_id=f"wf-{ticket.lower()}-001",
            workflow_name="FeatureDevelopmentWorkflow",
            step=step,
            agent=agent,
            status=status,
            pct=round(pct, 1),
            elapsed_ms=random.randint(1000, 120000),
            retry_count=random.randint(0, 2) if status == ExecStatus.RETRYING else 0,
            error="Claude API timeout after 3 retries" if status == ExecStatus.FAILED else None,
            jira_url=f"{jira_base}/{ticket}",
            temporal_url=f"http://localhost:8233/namespaces/default/workflows/wf-{ticket.lower()}-001",
        ))

    print("✅ Demo events injected. Starting console (Ctrl+C to exit)...")

def run():
    inject_demo_events()
    run_live_console(fetch_snapshot=build_snapshot, refresh_seconds=3.0)

if __name__ == "__main__":
    run()
