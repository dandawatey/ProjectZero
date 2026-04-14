"""Roll-up engine: events -> StatusSnapshot — PRJ0-56."""
from __future__ import annotations
from ..models.events import (
    ExecStatus, ExecutionEvent, StatusSnapshot, FeatureStatus,
    EpicStatus, TicketStatus, WorkflowStatus, StepStatus,
)
from . import event_store


def _rollup_status(statuses: list[ExecStatus]) -> ExecStatus:
    if ExecStatus.FAILED in statuses: return ExecStatus.FAILED
    if ExecStatus.BLOCKED in statuses: return ExecStatus.BLOCKED
    if ExecStatus.RUNNING in statuses: return ExecStatus.RUNNING
    if ExecStatus.RETRYING in statuses: return ExecStatus.RETRYING
    if all(s == ExecStatus.SUCCESS for s in statuses) and statuses: return ExecStatus.SUCCESS
    if all(s == ExecStatus.QUEUED for s in statuses) and statuses: return ExecStatus.QUEUED
    return ExecStatus.QUEUED


def _rollup_pct(pcts: list[float]) -> float:
    return round(sum(pcts) / len(pcts), 1) if pcts else 0.0


# Hard-coded feature->epic->ticket hierarchy for PRJ0
# In production this comes from JIRA. For demo/rollup purposes we use this map.
FEATURE_MAP = {
    "Platform Infrastructure": {
        "epics": {"EPIC-INFRA": ["PRJ0-1","PRJ0-3","PRJ0-4","PRJ0-5","PRJ0-6","PRJ0-12","PRJ0-25"]},
    },
    "Integration Services": {
        "epics": {"EPIC-INT": ["PRJ0-7","PRJ0-8","PRJ0-9","PRJ0-11","PRJ0-32","PRJ0-41","PRJ0-54","PRJ0-55"]},
    },
    "Agent System": {
        "epics": {"EPIC-AGENT": ["PRJ0-10","PRJ0-44","PRJ0-49","PRJ0-50","PRJ0-51","PRJ0-52","PRJ0-53"]},
    },
    "Governance & Quality": {
        "epics": {"EPIC-GOV": ["PRJ0-34","PRJ0-35","PRJ0-36","PRJ0-37","PRJ0-38","PRJ0-43","PRJ0-45","PRJ0-46"]},
    },
    "UI/UX & Product Workflow": {
        "epics": {"EPIC-UI": ["PRJ0-18","PRJ0-22","PRJ0-23","PRJ0-24","PRJ0-26","PRJ0-27","PRJ0-28","PRJ0-29","PRJ0-30","PRJ0-31","PRJ0-47"]},
    },
    "Observability & Reporting": {
        "epics": {"EPIC-OBS": ["PRJ0-19","PRJ0-20","PRJ0-21","PRJ0-39","PRJ0-48","PRJ0-56"]},
    },
}


def build_snapshot(jira_hierarchy: list[dict] | None = None) -> StatusSnapshot:
    """Build StatusSnapshot from event store + optional JIRA hierarchy."""
    tickets_raw = event_store.latest_per_ticket()
    ticket_map = {r["ticket_id"]: r for r in tickets_raw}
    workflows_raw = event_store.latest_per_workflow()
    wf_map = {r["workflow_run_id"]: r for r in workflows_raw}

    features = []
    for fname, fdata in FEATURE_MAP.items():
        f_epics = []
        for epic_key, ticket_keys in fdata["epics"].items():
            tickets = []
            for tkey in ticket_keys:
                ev = ticket_map.get(tkey)
                if ev:
                    status = ExecStatus(ev["status"])
                    pct = ev["pct"] or 0.0
                    wf = None
                    if ev.get("workflow_run_id") and ev["workflow_run_id"] in wf_map:
                        w = wf_map[ev["workflow_run_id"]]
                        wf = WorkflowStatus(
                            run_id=w["workflow_run_id"],
                            workflow_name=w.get("workflow_name",""),
                            ticket_id=tkey,
                            status=ExecStatus(w["status"]),
                            pct=w["pct"] or 0.0,
                            temporal_url=w.get("temporal_url"),
                        )
                    tickets.append(TicketStatus(
                        key=tkey,
                        summary=ev.get("step","") or tkey,
                        status=status,
                        pct=pct,
                        workflow=wf,
                        jira_url=ev.get("jira_url"),
                    ))
                else:
                    tickets.append(TicketStatus(key=tkey, summary=tkey, status=ExecStatus.QUEUED))

            epic_statuses = [t.status for t in tickets]
            epic_pcts = [t.pct for t in tickets]
            f_epics.append(EpicStatus(
                key=epic_key,
                summary=epic_key,
                status=_rollup_status(epic_statuses),
                pct=_rollup_pct(epic_pcts),
                tickets=tickets,
            ))

        feature_statuses = [e.status for e in f_epics]
        feature_pcts = [e.pct for e in f_epics]
        features.append(FeatureStatus(
            name=fname,
            status=_rollup_status(feature_statuses),
            pct=_rollup_pct(feature_pcts),
            epics=f_epics,
        ))

    all_statuses = [t.status for f in features for e in f.epics for t in e.tickets]
    all_pcts = [t.pct for f in features for e in f.epics for t in e.tickets]

    return StatusSnapshot(
        features=features,
        overall_pct=_rollup_pct(all_pcts),
        running_count=sum(1 for s in all_statuses if s == ExecStatus.RUNNING),
        failed_count=sum(1 for s in all_statuses if s == ExecStatus.FAILED),
        queued_count=sum(1 for s in all_statuses if s == ExecStatus.QUEUED),
    )
