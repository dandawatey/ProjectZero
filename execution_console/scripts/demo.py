#!/usr/bin/env python3
"""
Streaming demo mode — no JIRA, no Temporal, no backend required.

Simulates a full Project Zero sprint lifecycle:
  QUEUED → RUNNING (with progress ticking up) → SUCCESS / FAILED / RETRYING

Run:
    python execution_console/scripts/demo.py

Flags:
    --speed <float>   Tick speed multiplier (default 1.0, higher = faster)
    --max-concurrent  Max parallel tickets (default 3)

CAVEMAN MODE:
  Start script. Fake data appear. Progress bars move. Tickets finish.
  Some tickets fail. Some retry. Watch full sprint from start to end.
  Press Ctrl+C anytime to stop.
"""
from __future__ import annotations
import argparse
import dataclasses
import random
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from execution_console.app.models.events import (
    ExecStatus, EpicStatus, FeatureStatus, StatusSnapshot,
    StepStatus, TicketStatus, WorkflowStatus,
)
from execution_console.app.renderers.rich_console import run_live_console

# ── Ticket definitions ────────────────────────────────────────────────────────
#  (key, epic, feature_name, summary, agent, step, duration_ticks, fail_chance)

TICKET_SPECS = [
    # Agent System
    ("PRJ0-49", "EPIC-AGENT", "Agent System",       "Implement impl-agent worker",           "impl-agent",    "impl_activity",   14, 0.10),
    ("PRJ0-50", "EPIC-AGENT", "Agent System",       "Spec agent scaffolding",                "spec-agent",    "spec_activity",   10, 0.05),
    ("PRJ0-51", "EPIC-AGENT", "Agent System",       "Architecture agent integration",        "arch-agent",    "arch_activity",   12, 0.08),
    ("PRJ0-52", "EPIC-AGENT", "Agent System",       "Deploy activity worker",                "deploy-agent",  "deploy_activity",  8, 0.05),
    ("PRJ0-53", "EPIC-AGENT", "Agent System",       "Agent dispatcher routing",              "impl-agent",    "impl_activity",   11, 0.10),
    # Governance & Quality
    ("PRJ0-34", "EPIC-GOV",   "Governance",         "MCRA 4-eye review workflow",            "review-agent",  "review_activity", 16, 0.15),
    ("PRJ0-35", "EPIC-GOV",   "Governance",         "Stage gate enforcement",                "impl-agent",    "impl_activity",    9, 0.05),
    ("PRJ0-36", "EPIC-GOV",   "Governance",         "TDD enforcement gate",                  "test-agent",    "impl_activity",   10, 0.08),
    ("PRJ0-37", "EPIC-GOV",   "Governance",         "Brain memory promotion",                "impl-agent",    "impl_activity",   13, 0.12),
    ("PRJ0-38", "EPIC-GOV",   "Governance",         "Approval gate workflow",                "review-agent",  "review_activity", 15, 0.20),
    # Integration Services
    ("PRJ0-7",  "EPIC-INT",   "Integrations",       "JIRA REST client",                      "impl-agent",    "impl_activity",    8, 0.05),
    ("PRJ0-8",  "EPIC-INT",   "Integrations",       "Confluence sync service",               "impl-agent",    "impl_activity",    9, 0.05),
    ("PRJ0-9",  "EPIC-INT",   "Integrations",       "Temporal worker bootstrap",             "impl-agent",    "impl_activity",   11, 0.10),
    ("PRJ0-32", "EPIC-INT",   "Integrations",       "Integration health monitor",            "impl-agent",    "impl_activity",    7, 0.05),
    # Observability
    ("PRJ0-19", "EPIC-OBS",   "Observability",      "Execution Console backend",             "impl-agent",    "impl_activity",   18, 0.08),
    ("PRJ0-20", "EPIC-OBS",   "Observability",      "Rich terminal renderer",                "impl-agent",    "impl_activity",   12, 0.05),
    ("PRJ0-56", "EPIC-OBS",   "Observability",      "Demo streaming simulation",             "impl-agent",    "impl_activity",   10, 0.05),
    # UI/UX
    ("PRJ0-22", "EPIC-UI",    "UI/UX",              "Control Tower React scaffold",          "deploy-agent",  "deploy_activity",  9, 0.08),
    ("PRJ0-23", "EPIC-UI",    "UI/UX",              "Activity monitor component",            "impl-agent",    "impl_activity",   11, 0.10),
    ("PRJ0-47", "EPIC-UI",    "UI/UX",              "PM slash commands",                     "impl-agent",    "impl_activity",    8, 0.05),
    # Platform Infrastructure
    ("PRJ0-1",  "EPIC-INFRA", "Platform",           "FastAPI backend skeleton",              "impl-agent",    "impl_activity",    7, 0.05),
    ("PRJ0-3",  "EPIC-INFRA", "Platform",           "Postgres + SQLAlchemy models",         "impl-agent",    "impl_activity",    9, 0.05),
    ("PRJ0-4",  "EPIC-INFRA", "Platform",           "Auth middleware",                       "impl-agent",    "impl_activity",    8, 0.08),
]

JIRA_BASE = "https://isourceinnovation.atlassian.net/browse"
TEMPORAL_BASE = "http://localhost:8233/namespaces/default/workflows"

FEATURE_DISPLAY = {
    "Agent System":    "🤖 Agent System",
    "Governance":      "🏛️  Governance & Quality",
    "Integrations":    "🔌 Integration Services",
    "Observability":   "📊 Observability & Reporting",
    "UI/UX":           "🖥️  UI/UX & Product Workflow",
    "Platform":        "🏗️  Platform Infrastructure",
}

EPIC_SUMMARIES = {
    "EPIC-AGENT": "Agent System (34 agents, 7 teams)",
    "EPIC-GOV":   "Governance Workflows",
    "EPIC-INT":   "External Integrations",
    "EPIC-OBS":   "Observability & Console",
    "EPIC-UI":    "Control Tower UI",
    "EPIC-INFRA": "Platform Core",
}


# ── State model ───────────────────────────────────────────────────────────────

@dataclasses.dataclass
class TState:
    key: str
    epic: str
    feature: str
    summary: str
    agent: str
    step: str
    duration_ticks: int        # ticks to complete (100 / duration = pct per tick)
    fail_chance: float

    status: ExecStatus = ExecStatus.QUEUED
    pct: float = 0.0
    started_tick: int = 0
    elapsed_ticks: int = 0
    retry_count: int = 0
    max_retries: int = 2
    error: Optional[str] = None

    @property
    def jira_url(self) -> str:
        return f"{JIRA_BASE}/{self.key}"

    @property
    def temporal_url(self) -> str:
        return f"{TEMPORAL_BASE}/wf-{self.key.lower()}-001"

    @property
    def elapsed_ms(self) -> int:
        return self.elapsed_ticks * 1500  # ~1.5s per tick

    def tick_progress(self) -> None:
        """Advance pct by one tick's worth of progress."""
        step_pct = 100.0 / self.duration_ticks
        noise = random.uniform(-step_pct * 0.2, step_pct * 0.3)
        self.pct = min(99.9, self.pct + step_pct + noise)
        self.elapsed_ticks += 1

    def attempt_complete(self) -> None:
        """Try to complete. May fail (triggers retry or final failure)."""
        if random.random() < self.fail_chance and self.retry_count < self.max_retries:
            self.status = ExecStatus.RETRYING
            self.retry_count += 1
            self.error = random.choice([
                "Claude API timeout after 3 retries",
                "Temporal activity heartbeat timeout",
                "Test coverage below 80% threshold",
                "JIRA transition failed: 403 Forbidden",
                "Spec validation failed: missing acceptance criteria",
            ])
            self.pct = max(10.0, self.pct - random.uniform(10, 25))
        elif random.random() < self.fail_chance * 0.5 and self.retry_count >= self.max_retries:
            self.status = ExecStatus.FAILED
            self.pct = round(self.pct, 1)
        else:
            self.status = ExecStatus.SUCCESS
            self.pct = 100.0
            self.error = None

    def recover_from_retry(self) -> None:
        """Move RETRYING → RUNNING after 1-tick pause."""
        self.status = ExecStatus.RUNNING
        self.error = None


class DemoStateManager:
    def __init__(self, max_concurrent: int = 3):
        self.tickets: list[TState] = [
            TState(
                key=k, epic=epic, feature=feat, summary=summ,
                agent=agent, step=step, duration_ticks=dur, fail_chance=fc,
            )
            for k, epic, feat, summ, agent, step, dur, fc in TICKET_SPECS
        ]
        self.max_concurrent = max_concurrent
        self.tick_count = 0
        self._retry_cooldown: dict[str, int] = {}  # key → tick when retry ends

    def _running(self) -> list[TState]:
        return [t for t in self.tickets if t.status == ExecStatus.RUNNING]

    def _retrying(self) -> list[TState]:
        return [t for t in self.tickets if t.status == ExecStatus.RETRYING]

    def _queued(self) -> list[TState]:
        return [t for t in self.tickets if t.status == ExecStatus.QUEUED]

    def tick(self) -> None:
        self.tick_count += 1

        # Recover retrying tickets after 2-tick cooldown
        for t in self._retrying():
            cooldown_end = self._retry_cooldown.get(t.key, 0)
            if self.tick_count >= cooldown_end:
                t.recover_from_retry()
            # else stays RETRYING

        # Advance running tickets
        for t in self._running():
            t.tick_progress()
            if t.pct >= 99.0:
                t.attempt_complete()
                if t.status == ExecStatus.RETRYING:
                    self._retry_cooldown[t.key] = self.tick_count + random.randint(1, 3)

        # Start queued tickets up to max_concurrent
        active_count = len(self._running()) + len(self._retrying())
        queued = self._queued()
        while active_count < self.max_concurrent and queued:
            next_t = queued.pop(0)
            next_t.status = ExecStatus.RUNNING
            next_t.started_tick = self.tick_count
            next_t.pct = random.uniform(1.0, 5.0)  # small initial progress
            active_count += 1

    def build_snapshot(self) -> StatusSnapshot:
        """Build StatusSnapshot from current in-memory state (no SQLite needed)."""
        ticket_map: dict[str, TState] = {t.key: t for t in self.tickets}

        # Group into feature → epic → ticket hierarchy
        feature_groups: dict[str, dict[str, list[TState]]] = {}
        for t in self.tickets:
            feature_groups.setdefault(t.feature, {}).setdefault(t.epic, []).append(t)

        FEATURE_ORDER = ["Agent System", "Governance", "Integrations", "Observability", "UI/UX", "Platform"]

        features: list[FeatureStatus] = []
        for fname in FEATURE_ORDER:
            if fname not in feature_groups:
                continue
            epic_map = feature_groups[fname]
            f_epics: list[EpicStatus] = []

            for epic_key, epic_tickets in epic_map.items():
                t_statuses: list[EpicStatus] = []
                tickets: list[TicketStatus] = []

                for t in epic_tickets:
                    step = _make_step(t)
                    wf = WorkflowStatus(
                        run_id=f"wf-{t.key.lower()}-001",
                        workflow_name="FeatureDevelopmentWorkflow",
                        ticket_id=t.key,
                        status=t.status,
                        pct=t.pct,
                        steps=[step],
                        temporal_url=t.temporal_url if t.status != ExecStatus.QUEUED else None,
                    )
                    tickets.append(TicketStatus(
                        key=t.key,
                        summary=t.summary,
                        status=t.status,
                        pct=t.pct,
                        workflow=wf,
                        jira_url=t.jira_url,
                    ))

                from execution_console.app.services.state_engine import _rollup_status, _rollup_pct
                epic_status = _rollup_status([tick.status for tick in tickets])
                epic_pct = _rollup_pct([tick.pct for tick in tickets])

                f_epics.append(EpicStatus(
                    key=epic_key,
                    summary=EPIC_SUMMARIES.get(epic_key, epic_key),
                    status=epic_status,
                    pct=epic_pct,
                    tickets=tickets,
                ))

            from execution_console.app.services.state_engine import _rollup_status, _rollup_pct
            feat_status = _rollup_status([e.status for e in f_epics])
            feat_pct = _rollup_pct([e.pct for e in f_epics])

            features.append(FeatureStatus(
                name=FEATURE_DISPLAY.get(fname, fname),
                status=feat_status,
                pct=feat_pct,
                epics=f_epics,
            ))

        all_tickets = [t for f in features for e in f.epics for t in e.tickets]
        all_pcts = [t.pct for t in all_tickets]
        all_statuses = [t.status for t in all_tickets]

        from execution_console.app.services.state_engine import _rollup_pct
        return StatusSnapshot(
            features=features,
            overall_pct=_rollup_pct(all_pcts),
            running_count=sum(1 for s in all_statuses if s == ExecStatus.RUNNING),
            failed_count=sum(1 for s in all_statuses if s == ExecStatus.FAILED),
            queued_count=sum(1 for s in all_statuses if s == ExecStatus.QUEUED),
        )

    def is_complete(self) -> bool:
        return all(
            t.status in (ExecStatus.SUCCESS, ExecStatus.FAILED, ExecStatus.CANCELLED)
            for t in self.tickets
        )


def _make_step(t: TState) -> StepStatus:
    return StepStatus(
        name=t.step,
        status=t.status,
        agent=t.agent,
        pct=t.pct,
        elapsed_ms=t.elapsed_ms if t.status != ExecStatus.QUEUED else None,
        retry_count=t.retry_count,
        error=t.error,
    )


# ── Entry point ───────────────────────────────────────────────────────────────

def run(speed: float = 1.0, max_concurrent: int = 3):
    state = DemoStateManager(max_concurrent=max_concurrent)
    tick_interval = max(0.3, 1.5 / speed)

    last_tick_at = [time.time()]

    def fetch_snapshot() -> StatusSnapshot:
        nonlocal last_tick_at
        now = time.time()
        if now - last_tick_at[0] >= tick_interval:
            state.tick()
            last_tick_at[0] = now
        return state.build_snapshot()

    from rich.console import Console
    Console().print(
        "\n[bold cyan]ProjectZero Execution Console[/bold cyan] — [dim]Demo Mode[/dim]\n"
        f"[grey50]{len(TICKET_SPECS)} tickets · {max_concurrent} max concurrent · "
        f"{speed}x speed · Ctrl+C to stop[/grey50]\n"
    )
    time.sleep(1.0)

    run_live_console(fetch_snapshot=fetch_snapshot, refresh_seconds=0.8)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ProjectZero Execution Console — Demo Mode")
    parser.add_argument("--speed", type=float, default=1.0, help="Simulation speed multiplier")
    parser.add_argument("--max-concurrent", type=int, default=3, help="Max parallel tickets")
    args = parser.parse_args()
    run(speed=args.speed, max_concurrent=args.max_concurrent)
