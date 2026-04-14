"""
HTML report generator — renders StatusSnapshot as a self-contained HTML file — PRJ0-56.

NORMAL MODE:
  Serializes the StatusSnapshot into a single-file HTML with embedded CSS.
  No JS frameworks, no CDN dependencies. Opens in any browser.
  Useful for: sharing status snapshots, CI artifacts, async stakeholder updates.

CAVEMAN MODE:
  We take current state. We write one HTML file.
  You open file in browser. See same tree as terminal. Share with anyone.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.events import ExecStatus, StatusSnapshot

STATUS_COLOR = {
    ExecStatus.QUEUED:    "#888888",
    ExecStatus.RUNNING:   "#00bcd4",
    ExecStatus.SUCCESS:   "#4caf50",
    ExecStatus.FAILED:    "#f44336",
    ExecStatus.BLOCKED:   "#ff9800",
    ExecStatus.RETRYING:  "#ff5722",
    ExecStatus.CANCELLED: "#607d8b",
}

STATUS_ICON = {
    ExecStatus.QUEUED:    "⬜",
    ExecStatus.RUNNING:   "🔄",
    ExecStatus.SUCCESS:   "✅",
    ExecStatus.FAILED:    "❌",
    ExecStatus.BLOCKED:   "🚧",
    ExecStatus.RETRYING:  "🔁",
    ExecStatus.CANCELLED: "⛔",
}


def _pct_bar(pct: float) -> str:
    filled = int(pct / 100 * 20)
    empty = 20 - filled
    return f"{'█' * filled}{'░' * empty}"


def _badge(status: ExecStatus) -> str:
    color = STATUS_COLOR.get(status, "#888")
    icon = STATUS_ICON.get(status, "?")
    return (
        f'<span style="background:{color};color:white;padding:2px 8px;'
        f'border-radius:4px;font-size:0.8em">{icon} {status.value}</span>'
    )


def _link(url: Optional[str], label: str) -> str:
    if url:
        return f'<a href="{url}" target="_blank" style="color:#00bcd4">{label}</a>'
    return label


def _progress_bar(pct: float, color: str = "#00bcd4") -> str:
    return (
        f'<div style="background:#333;border-radius:4px;height:8px;width:200px;display:inline-block">'
        f'<div style="background:{color};width:{pct:.0f}%;height:8px;border-radius:4px"></div>'
        f"</div> <span style='color:{color}'>{pct:.0f}%</span>"
    )


def generate(snapshot: StatusSnapshot, output_path: Optional[str] = None) -> str:
    """Generate HTML report. Returns HTML string. Writes to output_path if given."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    rows = []
    for feature in snapshot.features:
        f_color = STATUS_COLOR.get(feature.status, "#888")
        rows.append(
            f'<tr style="background:#1e1e2e">'
            f'<td style="padding:8px 12px;color:{f_color};font-weight:bold">'
            f'{STATUS_ICON.get(feature.status,"?")} {feature.name}</td>'
            f'<td>{_badge(feature.status)}</td>'
            f'<td>{_progress_bar(feature.pct, f_color)}</td>'
            f'<td></td></tr>'
        )
        for epic in feature.epics:
            e_color = STATUS_COLOR.get(epic.status, "#888")
            rows.append(
                f'<tr style="background:#181825">'
                f'<td style="padding:6px 12px 6px 28px;color:{e_color}">'
                f'📦 <strong>{epic.key}</strong> <span style="color:#888">{epic.summary}</span></td>'
                f'<td>{_badge(epic.status)}</td>'
                f'<td>{_progress_bar(epic.pct, e_color)}</td>'
                f'<td></td></tr>'
            )
            for ticket in epic.tickets:
                t_color = STATUS_COLOR.get(ticket.status, "#888")
                jira_cell = _link(ticket.jira_url, ticket.key) if ticket.jira_url else ticket.key
                wf_cell = ""
                if ticket.workflow:
                    w = ticket.workflow
                    wf_cell = _link(w.temporal_url, f"{w.workflow_name[:24]}…") if w.temporal_url else w.workflow_name[:24]
                rows.append(
                    f'<tr style="background:#13131f">'
                    f'<td style="padding:5px 12px 5px 48px;color:{t_color}">'
                    f'{STATUS_ICON.get(ticket.status,"?")} {jira_cell} '
                    f'<span style="color:#666;font-size:0.85em">{ticket.summary}</span></td>'
                    f'<td>{_badge(ticket.status)}</td>'
                    f'<td>{_progress_bar(ticket.pct, t_color)}</td>'
                    f'<td style="color:#555;font-size:0.8em">{wf_cell}</td></tr>'
                )

    failed = [
        t for f in snapshot.features for e in f.epics
        for t in e.tickets if t.status == ExecStatus.FAILED
    ]
    failed_section = ""
    if failed:
        failed_rows = "".join(
            f'<li style="margin:6px 0"><span style="color:#f44336">❌ {t.key}</span> '
            f'<span style="color:#888">{t.summary}</span></li>'
            for t in failed
        )
        failed_section = (
            f'<div style="border:1px solid #f44336;border-radius:6px;padding:16px;margin-top:24px">'
            f'<h3 style="color:#f44336;margin:0 0 12px">FAILED ITEMS</h3>'
            f'<ul style="margin:0;padding-left:16px">{failed_rows}</ul></div>'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ProjectZero Execution Console — {now}</title>
  <style>
    body {{ background:#0d0d1a; color:#cdd6f4; font-family:'Courier New',monospace; margin:0; padding:24px }}
    h1 {{ color:#cba6f7; margin-bottom:4px }}
    .subtitle {{ color:#888; margin-bottom:24px }}
    .header-stats {{ display:flex; gap:24px; margin-bottom:24px }}
    .stat {{ background:#181825; padding:12px 20px; border-radius:6px; text-align:center }}
    .stat-value {{ font-size:2em; font-weight:bold }}
    .running {{ color:#00bcd4 }} .success {{ color:#4caf50 }}
    .failed {{ color:#f44336 }} .queued {{ color:#888 }}
    table {{ width:100%; border-collapse:collapse }}
    th {{ background:#1e1e2e; color:#888; padding:8px 12px; text-align:left; font-weight:normal }}
    tr:hover {{ background:#252535 !important }}
  </style>
</head>
<body>
  <h1>ProjectZero Execution Console</h1>
  <div class="subtitle">Generated {now}</div>
  <div class="header-stats">
    <div class="stat"><div class="stat-value">{snapshot.overall_pct:.0f}%</div><div>Overall</div></div>
    <div class="stat"><div class="stat-value running">{snapshot.running_count}</div><div>Running</div></div>
    <div class="stat"><div class="stat-value success">{sum(1 for f in snapshot.features for e in f.epics for t in e.tickets if t.status==ExecStatus.SUCCESS)}</div><div>Done</div></div>
    <div class="stat"><div class="stat-value failed">{snapshot.failed_count}</div><div>Failed</div></div>
    <div class="stat"><div class="stat-value queued">{snapshot.queued_count}</div><div>Queued</div></div>
  </div>
  <table>
    <thead><tr>
      <th>Feature / Epic / Ticket</th><th>Status</th><th>Progress</th><th>Workflow</th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  {failed_section}
</body>
</html>"""

    if output_path:
        Path(output_path).write_text(html, encoding="utf-8")

    return html
