"""Rich renderer tests — PRJ0-70."""
import pytest
from rich.console import Console

from execution_console.app.models.events import (
    ExecStatus, StatusSnapshot, FeatureStatus, EpicStatus, TicketStatus
)
from execution_console.app.renderers.rich_console import build_layout, _pct_bar, _status_badge


def _make_snapshot(overall_pct=50.0, running=1, failed=0, queued=5) -> StatusSnapshot:
    ticket = TicketStatus(key="PRJ0-49", summary="Test ticket", status=ExecStatus.RUNNING, pct=50.0)
    epic = EpicStatus(key="EPIC-AGENT", summary="Agent System", status=ExecStatus.RUNNING, pct=50.0, tickets=[ticket])
    feature = FeatureStatus(name="Agent System", status=ExecStatus.RUNNING, pct=50.0, epics=[epic])
    return StatusSnapshot(
        features=[feature],
        overall_pct=overall_pct,
        running_count=running,
        failed_count=failed,
        queued_count=queued,
    )


def test_pct_bar_full():
    bar = _pct_bar(100.0)
    assert "█" in bar
    assert "░" not in bar


def test_pct_bar_empty():
    bar = _pct_bar(0.0)
    assert "░" in bar
    assert "█" not in bar


def test_pct_bar_half():
    bar = _pct_bar(50.0)
    assert "█" in bar
    assert "░" in bar


def test_pct_bar_default_width():
    bar = _pct_bar(100.0, 18)
    # 18 filled blocks
    assert bar.count("█") == 18


def test_status_badge_running():
    text = _status_badge(ExecStatus.RUNNING)
    assert "RUNNING" in text.plain


def test_status_badge_failed():
    text = _status_badge(ExecStatus.FAILED)
    assert "FAILED" in text.plain


def test_status_badge_success():
    text = _status_badge(ExecStatus.SUCCESS)
    assert "SUCCESS" in text.plain


def test_status_badge_queued():
    text = _status_badge(ExecStatus.QUEUED)
    assert "QUEUED" in text.plain


def test_build_layout_returns_table():
    snap = _make_snapshot()
    layout = build_layout(snap)
    assert layout is not None


def test_build_layout_no_exception():
    """build_layout must not raise for any valid snapshot."""
    snap = _make_snapshot(overall_pct=63.0, running=2, failed=1, queued=3)
    console = Console(force_terminal=False, width=120)
    with console.capture():
        console.print(build_layout(snap))


def test_build_layout_failed_panel():
    """FAILED ITEMS panel appears when there are failed tickets."""
    ticket = TicketStatus(key="PRJ0-99", summary="Broken", status=ExecStatus.FAILED, pct=0.0)
    epic = EpicStatus(key="EPIC-TEST", summary="Test", status=ExecStatus.FAILED, pct=0.0, tickets=[ticket])
    feature = FeatureStatus(name="Agent System", status=ExecStatus.FAILED, pct=0.0, epics=[epic])
    snap = StatusSnapshot(
        features=[feature],
        overall_pct=0.0,
        running_count=0,
        failed_count=1,
        queued_count=0,
    )
    layout = build_layout(snap)
    console = Console(force_terminal=False, width=120)
    with console.capture() as capture:
        console.print(layout)
    output = capture.get()
    assert "PRJ0-99" in output or "FAILED" in output


def test_build_layout_empty_snapshot():
    snap = StatusSnapshot(features=[], overall_pct=0.0, running_count=0, failed_count=0, queued_count=0)
    layout = build_layout(snap)
    assert layout is not None


def test_build_layout_all_success():
    """Snapshot with all success renders without crash."""
    ticket = TicketStatus(key="PRJ0-1", summary="Done", status=ExecStatus.SUCCESS, pct=100.0)
    epic = EpicStatus(key="EPIC-INFRA", summary="Infra", status=ExecStatus.SUCCESS, pct=100.0, tickets=[ticket])
    feature = FeatureStatus(name="Platform Infrastructure", status=ExecStatus.SUCCESS, pct=100.0, epics=[epic])
    snap = StatusSnapshot(
        features=[feature],
        overall_pct=100.0,
        running_count=0,
        failed_count=0,
        queued_count=0,
    )
    console = Console(force_terminal=False, width=120)
    with console.capture():
        console.print(build_layout(snap))


def test_build_layout_running_tickets_panel():
    """Running tickets trigger LIVE EXECUTION panel."""
    ticket = TicketStatus(key="PRJ0-49", summary="Running now", status=ExecStatus.RUNNING, pct=55.0)
    epic = EpicStatus(key="EPIC-AGENT", summary="Agents", status=ExecStatus.RUNNING, pct=55.0, tickets=[ticket])
    feature = FeatureStatus(name="Agent System", status=ExecStatus.RUNNING, pct=55.0, epics=[epic])
    snap = StatusSnapshot(
        features=[feature],
        overall_pct=55.0,
        running_count=1,
        failed_count=0,
        queued_count=5,
    )
    console = Console(force_terminal=False, width=120)
    with console.capture() as capture:
        console.print(build_layout(snap))
    output = capture.get()
    assert "PRJ0-49" in output
