"""ISO/IEC 42001:2023 audit service layer.

Handles:
- Risk register CRUD + auto-classification
- Transparency log writes (called from agent contribution hooks)
- Incident register CRUD
- Control assessment CRUD + Statement of Applicability generation
- Full audit report generation (JSON, Confluence-ready)
- Auto-seeding of ISO 42001 Annex A controls on first run
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.iso_audit import (
    AiRiskEntry,
    AiTransparencyLog,
    AiIncident,
    AiControlAssessment,
    ISO_42001_CONTROLS,
)


# ---------------------------------------------------------------------------
# Risk register
# ---------------------------------------------------------------------------

async def create_risk_entry(db: AsyncSession, data: dict) -> AiRiskEntry:
    entry = AiRiskEntry(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def list_risk_entries(
    db: AsyncSession,
    product_id: str | None = None,
    risk_level: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AiRiskEntry]:
    q = select(AiRiskEntry).order_by(AiRiskEntry.created_at.desc())
    if product_id:
        q = q.where(AiRiskEntry.product_id == product_id)
    if risk_level:
        q = q.where(AiRiskEntry.risk_level == risk_level)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars())


async def get_risk_entry(db: AsyncSession, entry_id: uuid.UUID) -> AiRiskEntry | None:
    result = await db.execute(select(AiRiskEntry).where(AiRiskEntry.id == entry_id))
    return result.scalar_one_or_none()


async def update_risk_entry(db: AsyncSession, entry_id: uuid.UUID, data: dict) -> AiRiskEntry | None:
    entry = await get_risk_entry(db, entry_id)
    if not entry:
        return None
    for k, v in data.items():
        if hasattr(entry, k):
            setattr(entry, k, v)
    await db.commit()
    await db.refresh(entry)
    return entry


# ---------------------------------------------------------------------------
# Transparency log
# ---------------------------------------------------------------------------

async def log_transparency(db: AsyncSession, data: dict) -> AiTransparencyLog:
    entry = AiTransparencyLog(**data)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def list_transparency_logs(
    db: AsyncSession,
    workflow_run_id: uuid.UUID | None = None,
    agent_type: str | None = None,
    decision_type: str | None = None,
    human_review_required: bool | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[AiTransparencyLog]:
    q = select(AiTransparencyLog).order_by(AiTransparencyLog.created_at.desc())
    if workflow_run_id:
        q = q.where(AiTransparencyLog.workflow_run_id == workflow_run_id)
    if agent_type:
        q = q.where(AiTransparencyLog.agent_type == agent_type)
    if decision_type:
        q = q.where(AiTransparencyLog.decision_type == decision_type)
    if human_review_required is not None:
        q = q.where(AiTransparencyLog.human_review_required == human_review_required)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars())


async def mark_transparency_reviewed(
    db: AsyncSession,
    log_id: int,
    reviewed_by: str,
    outcome_accepted: bool,
    rejection_reason: str | None = None,
) -> AiTransparencyLog | None:
    result = await db.execute(select(AiTransparencyLog).where(AiTransparencyLog.id == log_id))
    entry = result.scalar_one_or_none()
    if not entry:
        return None
    entry.human_reviewed = True
    entry.reviewed_by = reviewed_by
    entry.reviewed_at = datetime.now(timezone.utc)
    entry.outcome_accepted = outcome_accepted
    entry.rejection_reason = rejection_reason
    await db.commit()
    await db.refresh(entry)
    return entry


# ---------------------------------------------------------------------------
# Incident register
# ---------------------------------------------------------------------------

async def create_incident(db: AsyncSession, data: dict) -> AiIncident:
    incident = AiIncident(**data)
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


async def list_incidents(
    db: AsyncSession,
    status: str | None = None,
    severity: str | None = None,
    incident_type: str | None = None,
    product_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AiIncident]:
    q = select(AiIncident).order_by(AiIncident.created_at.desc())
    if status:
        q = q.where(AiIncident.status == status)
    if severity:
        q = q.where(AiIncident.severity == severity)
    if incident_type:
        q = q.where(AiIncident.incident_type == incident_type)
    if product_id:
        q = q.where(AiIncident.product_id == product_id)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars())


async def update_incident(db: AsyncSession, incident_id: uuid.UUID, data: dict) -> AiIncident | None:
    result = await db.execute(select(AiIncident).where(AiIncident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        return None
    for k, v in data.items():
        if hasattr(incident, k):
            setattr(incident, k, v)
    await db.commit()
    await db.refresh(incident)
    return incident


# ---------------------------------------------------------------------------
# Control assessment (Annex A)
# ---------------------------------------------------------------------------

async def seed_controls(db: AsyncSession) -> int:
    """Seed all ISO 42001 Annex A controls if not already present. Returns count inserted."""
    existing = set(
        row[0]
        for row in (await db.execute(select(AiControlAssessment.control_id))).all()
    )

    CONTROL_CATEGORIES = {
        "A.2": "GOVERNANCE",
        "A.3": "GOVERNANCE",
        "A.4": "GOVERNANCE",
        "A.5": "GOVERNANCE",
        "A.6": "RISK",
        "A.7": "DATA",
        "A.8": "OVERSIGHT",
        "A.9": "TRANSPARENCY",
        "A.10": "ACCOUNTABILITY",
        "A.11": "THIRD_PARTY",
    }

    inserted = 0
    for control_id, control_name in ISO_42001_CONTROLS.items():
        if control_id in existing:
            continue
        clause = ".".join(control_id.split(".")[:2])
        category = CONTROL_CATEGORIES.get(clause, "GOVERNANCE")
        db.add(AiControlAssessment(
            control_id=control_id,
            control_name=control_name,
            control_clause=clause,
            control_category=category,
            status="not_assessed",
            is_applicable=True,
        ))
        inserted += 1

    if inserted:
        await db.commit()
    return inserted


async def list_controls(
    db: AsyncSession,
    status: str | None = None,
    category: str | None = None,
) -> list[AiControlAssessment]:
    q = select(AiControlAssessment).order_by(AiControlAssessment.control_id)
    if status:
        q = q.where(AiControlAssessment.status == status)
    if category:
        q = q.where(AiControlAssessment.control_category == category)
    result = await db.execute(q)
    return list(result.scalars())


async def upsert_control(db: AsyncSession, control_id: str, data: dict) -> AiControlAssessment:
    result = await db.execute(
        select(AiControlAssessment).where(AiControlAssessment.control_id == control_id)
    )
    control = result.scalar_one_or_none()
    if control:
        for k, v in data.items():
            if hasattr(control, k):
                setattr(control, k, v)
        control.last_assessed_at = datetime.now(timezone.utc)
    else:
        control = AiControlAssessment(control_id=control_id, **data)
        control.last_assessed_at = datetime.now(timezone.utc)
        db.add(control)
    await db.commit()
    await db.refresh(control)
    return control


# ---------------------------------------------------------------------------
# Audit report generator
# ---------------------------------------------------------------------------

async def generate_audit_report(db: AsyncSession, product_id: str | None = None) -> dict[str, Any]:
    """
    Generate a full ISO 42001 audit readiness report.

    Sections:
    1. Executive summary — control compliance scores + open incidents
    2. Statement of Applicability (SoA) — all controls with status
    3. Risk register summary — by level
    4. Transparency metrics — human review rates, acceptance rates
    5. Incident summary — by type and severity
    6. Gaps and remediation backlog
    """
    now = datetime.now(timezone.utc).isoformat()

    # --- Controls summary ---
    controls = await list_controls(db)
    total_controls = len(controls)
    compliant = sum(1 for c in controls if c.status == "COMPLIANT")
    partial = sum(1 for c in controls if c.status == "PARTIAL")
    non_compliant = sum(1 for c in controls if c.status == "NON_COMPLIANT")
    not_assessed = sum(1 for c in controls if c.status == "not_assessed")
    applicable = sum(1 for c in controls if c.is_applicable)
    compliance_pct = round((compliant / applicable * 100) if applicable else 0, 1)

    soa = [
        {
            "control_id": c.control_id,
            "control_name": c.control_name,
            "category": c.control_category,
            "applicable": c.is_applicable,
            "status": c.status,
            "score": c.compliance_score,
            "gap": c.gap_description,
            "remediation_owner": c.remediation_owner,
            "remediation_due": c.remediation_due.isoformat() if c.remediation_due else None,
            "last_assessed": c.last_assessed_at.isoformat() if c.last_assessed_at else None,
        }
        for c in controls
    ]

    # --- Risk register summary ---
    risk_q = select(AiRiskEntry.risk_level, func.count(AiRiskEntry.id)).group_by(AiRiskEntry.risk_level)
    if product_id:
        risk_q = risk_q.where(AiRiskEntry.product_id == product_id)
    risk_rows = await db.execute(risk_q)
    risk_by_level = {row[0]: row[1] for row in risk_rows}

    high_risk_q = select(
        AiRiskEntry.use_case, AiRiskEntry.risk_level, AiRiskEntry.human_oversight_level,
        AiRiskEntry.accountability_owner, AiRiskEntry.ai_model
    ).where(AiRiskEntry.risk_level.in_(["HIGH", "PROHIBITED"]))
    if product_id:
        high_risk_q = high_risk_q.where(AiRiskEntry.product_id == product_id)
    high_risk_rows = await db.execute(high_risk_q)
    high_risk_items = [
        {
            "use_case": r[0], "risk_level": r[1],
            "oversight": r[2], "owner": r[3], "model": r[4],
        }
        for r in high_risk_rows
    ]

    # --- Transparency metrics ---
    trans_base = select(AiTransparencyLog)
    if product_id:
        # Transparency logs don't have product_id — filter via workflow_run join if needed
        pass
    total_actions = (await db.execute(select(func.count()).select_from(AiTransparencyLog))).scalar_one()
    human_required = (await db.execute(
        select(func.count()).select_from(AiTransparencyLog)
        .where(AiTransparencyLog.human_review_required == True)
    )).scalar_one()
    human_done = (await db.execute(
        select(func.count()).select_from(AiTransparencyLog)
        .where(AiTransparencyLog.human_reviewed == True)
    )).scalar_one()
    outcome_accepted = (await db.execute(
        select(func.count()).select_from(AiTransparencyLog)
        .where(AiTransparencyLog.outcome_accepted == True)
    )).scalar_one()
    outcome_rejected = (await db.execute(
        select(func.count()).select_from(AiTransparencyLog)
        .where(AiTransparencyLog.outcome_accepted == False)
    )).scalar_one()

    pending_reviews = human_required - human_done
    review_completion_pct = round((human_done / human_required * 100) if human_required else 100, 1)
    acceptance_rate_pct = round(
        (outcome_accepted / (outcome_accepted + outcome_rejected) * 100)
        if (outcome_accepted + outcome_rejected) else 0,
        1,
    )

    # --- Incident summary ---
    inc_q = select(AiIncident.severity, AiIncident.status, func.count(AiIncident.id))
    inc_q = inc_q.group_by(AiIncident.severity, AiIncident.status)
    if product_id:
        inc_q = inc_q.where(AiIncident.product_id == product_id)
    inc_rows = await db.execute(inc_q)

    incidents_summary: dict[str, Any] = {}
    total_incidents = 0
    open_critical = 0
    for row in inc_rows:
        severity, status, count = row
        total_incidents += count
        if severity == "CRITICAL" and status == "open":
            open_critical += count
        incidents_summary.setdefault(severity, {})[status] = count

    # --- Gap backlog ---
    gap_controls = [
        {
            "control_id": c.control_id,
            "control_name": c.control_name,
            "status": c.status,
            "gap": c.gap_description,
            "risk": c.risk_if_unaddressed,
            "owner": c.remediation_owner,
            "due": c.remediation_due.isoformat() if c.remediation_due else None,
        }
        for c in controls
        if c.status in ("NON_COMPLIANT", "PARTIAL") and c.is_applicable
    ]

    # --- Assemble report ---
    report: dict[str, Any] = {
        "report_type": "ISO/IEC 42001:2023 AI Management System — Audit Readiness Report",
        "generated_at": now,
        "product_id": product_id or "factory-wide",
        "executive_summary": {
            "overall_compliance_pct": compliance_pct,
            "controls": {
                "total": total_controls,
                "applicable": applicable,
                "compliant": compliant,
                "partial": partial,
                "non_compliant": non_compliant,
                "not_assessed": not_assessed,
            },
            "open_critical_incidents": open_critical,
            "pending_human_reviews": pending_reviews,
            "ai_outcome_acceptance_rate_pct": acceptance_rate_pct,
            "audit_readiness": _readiness_rating(compliance_pct, open_critical, pending_reviews),
        },
        "statement_of_applicability": soa,
        "risk_register_summary": {
            "by_level": risk_by_level,
            "high_risk_items": high_risk_items,
        },
        "transparency_metrics": {
            "total_ai_actions": total_actions,
            "requiring_human_review": human_required,
            "human_reviews_completed": human_done,
            "review_completion_pct": review_completion_pct,
            "outcomes_accepted": outcome_accepted,
            "outcomes_rejected": outcome_rejected,
            "acceptance_rate_pct": acceptance_rate_pct,
        },
        "incident_summary": {
            "total": total_incidents,
            "by_severity_and_status": incidents_summary,
            "open_critical": open_critical,
        },
        "gap_remediation_backlog": gap_controls,
    }

    return report


def _readiness_rating(compliance_pct: float, open_critical: int, pending_reviews: int) -> str:
    """Simple traffic-light audit readiness rating."""
    if open_critical > 0:
        return "RED — Critical incidents open. Not audit-ready."
    if compliance_pct >= 80 and pending_reviews == 0:
        return "GREEN — Audit ready."
    if compliance_pct >= 60:
        return "AMBER — Mostly compliant. Address gaps before audit."
    return "RED — Significant gaps. Not audit-ready."
