"""Rich terminal renderer for Claude Execution Console — PRJ0-56."""
from __future__ import annotations
import time
from datetime import datetime
from typing import Optional

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from ..models.events import ExecStatus, StatusSnapshot

STATUS_ICON = {
    ExecStatus.QUEUED:    ("⬜", "white"),
    ExecStatus.RUNNING:   ("🔄", "cyan"),
    ExecStatus.SUCCESS:   ("✅", "green"),
    ExecStatus.FAILED:    ("❌", "red"),
    ExecStatus.BLOCKED:   ("🚧", "yellow"),
    ExecStatus.RETRYING:  ("🔁", "orange3"),
    ExecStatus.CANCELLED: ("⛔", "grey50"),
}


def _hyperlink(url: str, label: str) -> str:
    """OSC 8 terminal hyperlink — falls back to plain text if not supported."""
    if url:
        return f"\x1b]8;;{url}\x1b\\{label}\x1b]8;;\x1b\\"
    return label


def _pct_bar(pct: float, width: int = 20) -> str:
    filled = int(pct / 100 * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}]"


def _status_text(status: ExecStatus) -> Text:
    icon, color = STATUS_ICON.get(status, ("?", "white"))
    return Text(f"{icon} {status.value}", style=color)


def build_layout(snapshot: StatusSnapshot) -> Table:
    """Build the main console layout as a Rich Table."""
    root = Table.grid(padding=(0, 1))
    root.add_column(ratio=1)

    # ── Header ─────────────────────────────────────────────────────────────
    header = Panel(
        f"[bold cyan]ProjectZero Execution Console[/bold cyan]  "
        f"[grey50]{datetime.utcnow().strftime('%H:%M:%S UTC')}[/grey50]\n"
        f"Overall Progress: [bold]{_pct_bar(snapshot.overall_pct)}[/bold] "
        f"[bold green]{snapshot.overall_pct:.1f}%[/bold green]  "
        f"[cyan]🔄 {snapshot.running_count} Running[/cyan]  "
        f"[red]❌ {snapshot.failed_count} Failed[/red]  "
        f"[white]⬜ {snapshot.queued_count} Queued[/white]",
        box=box.HORIZONTALS,
    )
    root.add_row(header)

    # ── Feature tree ────────────────────────────────────────────────────────
    tree_table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold dim",
        expand=True,
    )
    tree_table.add_column("Feature / Epic / Ticket", ratio=4)
    tree_table.add_column("Status", width=14)
    tree_table.add_column("Progress", width=24)
    tree_table.add_column("Agent / Details", ratio=2)

    for feature in snapshot.features:
        f_icon, f_color = STATUS_ICON.get(feature.status, ("?", "white"))
        tree_table.add_row(
            f"[bold {f_color}]{f_icon} {feature.name}[/bold {f_color}]",
            _status_text(feature.status),
            f"[{f_color}]{_pct_bar(feature.pct, 16)} {feature.pct:.0f}%[/{f_color}]",
            "",
        )
        for epic in feature.epics:
            e_icon, e_color = STATUS_ICON.get(epic.status, ("?", "white"))
            tree_table.add_row(
                f"  [dim]{e_icon}[/dim] [bold]{epic.key}[/bold] [dim]{epic.summary}[/dim]",
                _status_text(epic.status),
                f"[dim]{_pct_bar(epic.pct, 14)} {epic.pct:.0f}%[/dim]",
                "",
            )
            for ticket in epic.tickets:
                t_icon, t_color = STATUS_ICON.get(ticket.status, ("?", "white"))
                jira_link = _hyperlink(ticket.jira_url or "", ticket.key) if ticket.jira_url else ticket.key
                wf_info = ""
                if ticket.workflow:
                    w = ticket.workflow
                    wf_link = _hyperlink(w.temporal_url or "", w.workflow_name[:20]) if w.temporal_url else (w.workflow_name[:20] if w.workflow_name else "")
                    wf_info = wf_link
                tree_table.add_row(
                    f"    [{t_color}]{t_icon}[/{t_color}] {jira_link}",
                    _status_text(ticket.status),
                    f"[{t_color}]{_pct_bar(ticket.pct, 12)} {ticket.pct:.0f}%[/{t_color}]",
                    f"[dim]{wf_info}[/dim]",
                )

    root.add_row(tree_table)

    # ── Failed items ─────────────────────────────────────────────────────────
    failed = [
        t for f in snapshot.features for e in f.epics
        for t in e.tickets if t.status == ExecStatus.FAILED
    ]
    if failed:
        fail_table = Table(box=box.SIMPLE, show_header=False, expand=True)
        fail_table.add_column()
        for t in failed:
            fail_table.add_row(f"[red]❌ {t.key}[/red] [dim]{t.summary}[/dim]")
        root.add_row(Panel(fail_table, title="[red bold]FAILED ITEMS[/red bold]", border_style="red"))

    return root


def run_live_console(fetch_snapshot, refresh_seconds: float = 2.0):
    """Run Rich Live console. fetch_snapshot() -> StatusSnapshot called on each refresh."""
    console = Console()
    with Live(console=console, refresh_per_second=1, screen=False) as live:
        while True:
            try:
                snapshot = fetch_snapshot()
                live.update(build_layout(snapshot))
            except Exception as exc:
                live.update(Panel(f"[red]Error fetching snapshot: {exc}[/red]"))
            time.sleep(refresh_seconds)
