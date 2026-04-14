"""
Rich terminal renderer — Claude Execution Console — PRJ0-56.

Layout (top → bottom):
  1. Header bar      — title, timestamp, overall progress
  2. Live Execution  — currently running tickets (agent, step, elapsed, retries)
  3. Feature tree    — Feature > Epic > Ticket rows with status + progress
  4. Failed panel    — failed items with error messages (shown only if any)
"""
from __future__ import annotations
import time
from datetime import datetime
from typing import Optional

from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models.events import ExecStatus, StatusSnapshot, TicketStatus

# ── Status display maps ──────────────────────────────────────────────────────

STATUS_ICON = {
    ExecStatus.QUEUED:    ("⬜", "white"),
    ExecStatus.RUNNING:   ("🔄", "cyan"),
    ExecStatus.SUCCESS:   ("✅", "green"),
    ExecStatus.FAILED:    ("❌", "red"),
    ExecStatus.BLOCKED:   ("🚧", "yellow"),
    ExecStatus.RETRYING:  ("🔁", "orange3"),
    ExecStatus.CANCELLED: ("⛔", "grey50"),
}

STATUS_COLOR = {
    ExecStatus.QUEUED:    "white",
    ExecStatus.RUNNING:   "cyan",
    ExecStatus.SUCCESS:   "green",
    ExecStatus.FAILED:    "red",
    ExecStatus.BLOCKED:   "yellow",
    ExecStatus.RETRYING:  "orange3",
    ExecStatus.CANCELLED: "grey50",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _hyperlink(url: str, label: str) -> str:
    """OSC 8 terminal hyperlink — graceful fallback to plain text."""
    if url:
        return f"\x1b]8;;{url}\x1b\\{label}\x1b]8;;\x1b\\"
    return label


def _pct_bar(pct: float, width: int = 18) -> str:
    filled = max(0, min(width, int(pct / 100 * width)))
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}]"


def _elapsed(ms: Optional[int]) -> str:
    if ms is None:
        return ""
    s = ms // 1000
    m, sec = divmod(s, 60)
    return f"{m:02d}:{sec:02d}"


def _status_badge(status: ExecStatus) -> Text:
    icon, color = STATUS_ICON.get(status, ("?", "white"))
    return Text(f"{icon} {status.value:<10}", style=color)


def _running_tickets(snapshot: StatusSnapshot) -> list[TicketStatus]:
    return [
        t for f in snapshot.features for e in f.epics for t in e.tickets
        if t.status in (ExecStatus.RUNNING, ExecStatus.RETRYING)
    ]


# ── Layout builders ──────────────────────────────────────────────────────────

def _build_header(snapshot: StatusSnapshot) -> Panel:
    now = datetime.utcnow().strftime("%H:%M:%S UTC")
    overall_color = "red" if snapshot.failed_count > 0 else ("green" if snapshot.running_count == 0 else "cyan")
    bar = _pct_bar(snapshot.overall_pct, 24)

    line1 = (
        f"[bold cyan]ProjectZero Execution Console[/bold cyan]"
        f"  [grey50]{now}[/grey50]"
    )
    line2 = (
        f"Overall  [{overall_color}]{bar}[/{overall_color}] "
        f"[bold {overall_color}]{snapshot.overall_pct:.1f}%[/bold {overall_color}]   "
        f"[cyan]🔄 {snapshot.running_count} Running[/cyan]  "
        f"[green]✅ {sum(1 for f in snapshot.features for e in f.epics for t in e.tickets if t.status==ExecStatus.SUCCESS)} Done[/green]  "
        f"[red]❌ {snapshot.failed_count} Failed[/red]  "
        f"[white]⬜ {snapshot.queued_count} Queued[/white]"
    )
    return Panel(f"{line1}\n{line2}", box=box.HORIZONTALS, border_style="cyan")


def _build_live_execution(running: list[TicketStatus]) -> Optional[Panel]:
    if not running:
        return None

    t = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    t.add_column(width=6)   # icon
    t.add_column(width=10)  # key
    t.add_column(ratio=2)   # agent → step
    t.add_column(width=22)  # progress bar
    t.add_column(width=8)   # elapsed
    t.add_column(width=6)   # retries
    t.add_column(ratio=2)   # workflow link

    for ticket in running[:5]:  # show max 5 active tickets
        icon, color = STATUS_ICON.get(ticket.status, ("?", "white"))
        w = ticket.workflow
        agent_step = ""
        if w:
            step = w.steps[0].name if w.steps else ""
            agent = w.steps[0].agent if w.steps else ""
            agent_step = f"{agent} → {step}" if agent and step else (agent or step)
        elapsed = ""
        retries = ""
        wf_text = ""
        if w:
            elapsed = _elapsed(None)  # elapsed tracked externally in demo
            if w.steps and w.steps[0].elapsed_ms:
                elapsed = _elapsed(w.steps[0].elapsed_ms)
            if w.steps and w.steps[0].retry_count:
                retries = f"[orange3]↻{w.steps[0].retry_count}[/orange3]"
            if w.temporal_url:
                wf_text = _hyperlink(w.temporal_url, w.workflow_name[:20])
            else:
                wf_text = (w.workflow_name or "")[:20]

        bar = f"[{color}]{_pct_bar(ticket.pct, 14)} {ticket.pct:.0f}%[/{color}]"

        t.add_row(
            f"[{color}]{icon}[/{color}]",
            f"[bold {color}]{ticket.key}[/bold {color}]",
            f"[dim]{agent_step}[/dim]",
            bar,
            f"[grey50]{elapsed}[/grey50]",
            retries,
            f"[dim]{wf_text}[/dim]",
        )

    return Panel(t, title="[bold cyan]LIVE EXECUTION[/bold cyan]", border_style="cyan", box=box.ROUNDED)


def _build_feature_tree(snapshot: StatusSnapshot) -> Table:
    tree = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold dim",
        expand=True,
        padding=(0, 1),
    )
    tree.add_column("Feature / Epic / Ticket", ratio=4, no_wrap=False)
    tree.add_column("Status", width=16)
    tree.add_column("Progress", width=26)
    tree.add_column("Agent / Workflow", ratio=2)

    for feature in snapshot.features:
        f_color = STATUS_COLOR.get(feature.status, "white")
        icon, _ = STATUS_ICON.get(feature.status, ("?", "white"))

        # Skip features with all QUEUED + no events (reduces noise)
        has_activity = any(
            t.status != ExecStatus.QUEUED
            for e in feature.epics for t in e.tickets
        )

        tree.add_row(
            f"[bold {f_color}]{icon} {feature.name}[/bold {f_color}]",
            _status_badge(feature.status),
            f"[{f_color}]{_pct_bar(feature.pct, 16)} {feature.pct:.0f}%[/{f_color}]",
            "",
        )

        for epic in feature.epics:
            e_color = STATUS_COLOR.get(epic.status, "white")
            e_icon, _ = STATUS_ICON.get(epic.status, ("?", "white"))
            tree.add_row(
                f"  [dim]{e_icon}[/dim] [bold]{epic.key}[/bold] [grey50]{epic.summary}[/grey50]",
                _status_badge(epic.status),
                f"[dim {e_color}]{_pct_bar(epic.pct, 14)} {epic.pct:.0f}%[/dim {e_color}]",
                "",
            )

            for ticket in epic.tickets:
                t_color = STATUS_COLOR.get(ticket.status, "white")
                t_icon, _ = STATUS_ICON.get(ticket.status, ("?", "white"))

                # Jira link (OSC 8 if url available)
                key_display = _hyperlink(ticket.jira_url, ticket.key) if ticket.jira_url else ticket.key

                # Agent + workflow detail
                detail = ""
                if ticket.workflow:
                    w = ticket.workflow
                    if w.steps:
                        s = w.steps[0]
                        agent_part = f"[cyan]{s.agent}[/cyan]" if s.agent else ""
                        step_part = f"[dim]→ {s.name}[/dim]" if s.name else ""
                        retry_part = f"[orange3] ↻{s.retry_count}[/orange3]" if s.retry_count else ""
                        elapsed_part = f" [grey50]{_elapsed(s.elapsed_ms)}[/grey50]" if s.elapsed_ms else ""
                        detail = f"{agent_part}{step_part}{retry_part}{elapsed_part}"
                    elif w.workflow_name:
                        wf_link = _hyperlink(w.temporal_url, w.workflow_name[:22]) if w.temporal_url else w.workflow_name[:22]
                        detail = f"[dim]{wf_link}[/dim]"

                # Error for failed
                error_display = ""
                if ticket.status == ExecStatus.FAILED and ticket.workflow:
                    for s in ticket.workflow.steps:
                        if s.error:
                            error_display = f" [red dim]{s.error[:40]}[/red dim]"
                            break

                tree.add_row(
                    f"    [{t_color}]{t_icon}[/{t_color}] {key_display}"
                    f" [grey50 dim]{ticket.summary[:30]}[/grey50 dim]{error_display}",
                    _status_badge(ticket.status),
                    f"[{t_color}]{_pct_bar(ticket.pct, 12)} {ticket.pct:.0f}%[/{t_color}]",
                    detail,
                )

    return tree


def _build_failed_panel(snapshot: StatusSnapshot) -> Optional[Panel]:
    failed = [
        (t, e, f)
        for f in snapshot.features for e in f.epics
        for t in e.tickets if t.status == ExecStatus.FAILED
    ]
    if not failed:
        return None

    ft = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    ft.add_column(width=10)
    ft.add_column(ratio=3)
    ft.add_column(ratio=4)

    for ticket, epic, feature in failed:
        error_msg = ""
        if ticket.workflow:
            for s in ticket.workflow.steps:
                if s.error:
                    error_msg = s.error
                    break
        log_link = ""
        if ticket.workflow and ticket.workflow.steps and ticket.workflow.steps[0].log_url:
            log_link = _hyperlink(ticket.workflow.steps[0].log_url, "📋 logs")

        ft.add_row(
            f"[bold red]{ticket.key}[/bold red]",
            f"[white]{ticket.summary[:40]}[/white] [grey50]{feature.name}[/grey50]",
            f"[red dim]{error_msg[:60]}[/red dim] {log_link}",
        )

    return Panel(ft, title="[bold red]FAILED ITEMS[/bold red]", border_style="red", box=box.ROUNDED)


# ── Main layout assembler ────────────────────────────────────────────────────

def build_layout(snapshot: StatusSnapshot) -> Table:
    """Assemble full console layout as a Rich renderable."""
    root = Table.grid(padding=(0, 0))
    root.add_column(ratio=1)

    root.add_row(_build_header(snapshot))
    root.add_row("")  # spacer

    running = _running_tickets(snapshot)
    if running:
        live_panel = _build_live_execution(running)
        if live_panel:
            root.add_row(live_panel)
            root.add_row("")

    root.add_row(_build_feature_tree(snapshot))

    failed_panel = _build_failed_panel(snapshot)
    if failed_panel:
        root.add_row("")
        root.add_row(failed_panel)

    return root


# ── Live runner ──────────────────────────────────────────────────────────────

def run_live_console(fetch_snapshot, refresh_seconds: float = 2.0):
    """
    Run Rich Live console.
    fetch_snapshot() -> StatusSnapshot  called on each refresh cycle.
    Press Ctrl+C to exit.
    """
    console = Console()
    with Live(console=console, refresh_per_second=1, screen=False, transient=False) as live:
        while True:
            try:
                snapshot = fetch_snapshot()
                live.update(build_layout(snapshot))
            except Exception as exc:
                live.update(Panel(f"[red]Snapshot error: {exc}[/red]"))
            time.sleep(refresh_seconds)
