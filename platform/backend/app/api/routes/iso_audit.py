"""ISO/IEC 42001:2023 AI Audit Controls — API routes.

Endpoints:
  POST /iso-audit/risk-register              — log a risk entry
  GET  /iso-audit/risk-register              — list risk entries
  PATCH /iso-audit/risk-register/{id}        — update risk entry

  POST /iso-audit/transparency               — log a transparency entry
  GET  /iso-audit/transparency               — list transparency logs
  POST /iso-audit/transparency/{id}/review   — mark human review done

  POST /iso-audit/incidents                  — log an incident
  GET  /iso-audit/incidents                  — list incidents
  PATCH /iso-audit/incidents/{id}            — update incident (remediate/close)

  GET  /iso-audit/controls                   — list Annex A controls (SoA)
  POST /iso-audit/controls/{control_id}      — upsert control assessment
  POST /iso-audit/controls/seed              — seed all 18 Annex A controls

  GET  /iso-audit/report                     — generate full audit report (JSON)
  POST /iso-audit/report/publish             — publish report to Confluence
"""

from __future__ import annotations

import uuid
import os
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import iso_audit_service as svc

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class RiskEntryCreate(BaseModel):
    product_id: str | None = None
    workflow_run_id: uuid.UUID | None = None
    workflow_type: str | None = None
    risk_level: str                          # PROHIBITED | HIGH | LIMITED | MINIMAL
    use_case: str
    intended_purpose: str | None = None
    known_limitations: str | None = None
    data_inputs: list[str] | None = None
    personal_data_involved: bool = False
    sensitive_data_categories: list[str] | None = None
    human_oversight_level: str = "HUMAN_ON_LOOP"
    accountability_owner: str | None = None
    ai_model: str | None = None
    ai_provider: str | None = None
    model_version: str | None = None
    is_third_party_model: bool = True
    residual_risk: str | None = None
    mitigation_notes: str | None = None
    approved_by: str | None = None


class RiskEntryUpdate(BaseModel):
    risk_level: str | None = None
    human_oversight_level: str | None = None
    accountability_owner: str | None = None
    residual_risk: str | None = None
    mitigation_notes: str | None = None
    approved_by: str | None = None
    known_limitations: str | None = None


class TransparencyLogCreate(BaseModel):
    workflow_run_id: uuid.UUID | None = None
    agent_contribution_id: uuid.UUID | None = None
    correlation_id: str | None = None
    agent_id: str
    agent_type: str
    stage: str | None = None
    ai_model: str | None = None
    ai_provider: str | None = None
    decision_type: str
    prompt_category: str | None = None
    human_review_required: bool = False
    confidence_score: float | None = None
    reasoning_summary: str | None = None


class TransparencyReviewRequest(BaseModel):
    reviewed_by: str
    outcome_accepted: bool
    rejection_reason: str | None = None


class IncidentCreate(BaseModel):
    incident_type: str
    severity: str
    product_id: str | None = None
    workflow_run_id: uuid.UUID | None = None
    agent_id: str | None = None
    stage: str | None = None
    title: str
    description: str
    ai_involvement: str | None = None
    immediate_impact: str | None = None
    reported_by: str | None = None
    requires_regulatory_notification: bool = False


class IncidentUpdate(BaseModel):
    status: str | None = None
    root_cause: str | None = None
    corrective_action: str | None = None
    preventive_action: str | None = None
    lessons_learned: str | None = None
    assigned_to: str | None = None
    resolved_by: str | None = None
    regulatory_notified_at: str | None = None


class ControlAssessmentUpsert(BaseModel):
    control_name: str | None = None
    control_category: str | None = None
    is_applicable: bool = True
    exclusion_justification: str | None = None
    status: str = "not_assessed"
    compliance_score: int | None = None
    evidence: list[dict[str, str]] | None = None
    evidence_links: list[str] | None = None
    gap_description: str | None = None
    risk_if_unaddressed: str | None = None
    remediation_plan: str | None = None
    remediation_owner: str | None = None
    remediation_due: str | None = None
    remediation_status: str | None = None
    last_assessed_by: str | None = None
    assessment_notes: str | None = None
    next_assessment_due: str | None = None


# ---------------------------------------------------------------------------
# Risk register
# ---------------------------------------------------------------------------

@router.post("/risk-register", status_code=201)
async def create_risk_entry(body: RiskEntryCreate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    entry = await svc.create_risk_entry(db, data)
    return {"id": str(entry.id), "risk_level": entry.risk_level, "use_case": entry.use_case}


@router.get("/risk-register")
async def list_risk_entries(
    product_id: str | None = Query(None),
    risk_level: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    entries = await svc.list_risk_entries(db, product_id, risk_level, limit, offset)
    return [
        {
            "id": str(e.id),
            "product_id": e.product_id,
            "risk_level": e.risk_level,
            "use_case": e.use_case,
            "human_oversight_level": e.human_oversight_level,
            "accountability_owner": e.accountability_owner,
            "ai_model": e.ai_model,
            "residual_risk": e.residual_risk,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in entries
    ]


@router.patch("/risk-register/{entry_id}")
async def update_risk_entry(entry_id: uuid.UUID, body: RiskEntryUpdate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    entry = await svc.update_risk_entry(db, entry_id, data)
    if not entry:
        raise HTTPException(404, "Risk entry not found")
    return {"id": str(entry.id), "updated": True}


# ---------------------------------------------------------------------------
# Transparency log
# ---------------------------------------------------------------------------

@router.post("/transparency", status_code=201)
async def log_transparency(body: TransparencyLogCreate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    entry = await svc.log_transparency(db, data)
    return {"id": entry.id, "agent_id": entry.agent_id, "decision_type": entry.decision_type}


@router.get("/transparency")
async def list_transparency(
    workflow_run_id: uuid.UUID | None = Query(None),
    agent_type: str | None = Query(None),
    decision_type: str | None = Query(None),
    human_review_required: bool | None = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    logs = await svc.list_transparency_logs(
        db, workflow_run_id, agent_type, decision_type, human_review_required, limit, offset
    )
    return [
        {
            "id": log.id,
            "agent_id": log.agent_id,
            "agent_type": log.agent_type,
            "stage": log.stage,
            "ai_model": log.ai_model,
            "decision_type": log.decision_type,
            "human_review_required": log.human_review_required,
            "human_reviewed": log.human_reviewed,
            "outcome_accepted": log.outcome_accepted,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.post("/transparency/{log_id}/review")
async def review_transparency_log(
    log_id: int, body: TransparencyReviewRequest, db: AsyncSession = Depends(get_db)
):
    entry = await svc.mark_transparency_reviewed(
        db, log_id, body.reviewed_by, body.outcome_accepted, body.rejection_reason
    )
    if not entry:
        raise HTTPException(404, "Transparency log not found")
    return {"id": entry.id, "reviewed": True, "outcome_accepted": entry.outcome_accepted}


# ---------------------------------------------------------------------------
# Incident register
# ---------------------------------------------------------------------------

@router.post("/incidents", status_code=201)
async def create_incident(body: IncidentCreate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    incident = await svc.create_incident(db, data)
    return {
        "id": str(incident.id),
        "incident_type": incident.incident_type,
        "severity": incident.severity,
        "status": incident.status,
    }


@router.get("/incidents")
async def list_incidents(
    status: str | None = Query(None),
    severity: str | None = Query(None),
    incident_type: str | None = Query(None),
    product_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    incidents = await svc.list_incidents(db, status, severity, incident_type, product_id, limit, offset)
    return [
        {
            "id": str(i.id),
            "incident_type": i.incident_type,
            "severity": i.severity,
            "title": i.title,
            "status": i.status,
            "product_id": i.product_id,
            "agent_id": i.agent_id,
            "reported_by": i.reported_by,
            "assigned_to": i.assigned_to,
            "requires_regulatory_notification": i.requires_regulatory_notification,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in incidents
    ]


@router.patch("/incidents/{incident_id}")
async def update_incident(incident_id: uuid.UUID, body: IncidentUpdate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    incident = await svc.update_incident(db, incident_id, data)
    if not incident:
        raise HTTPException(404, "Incident not found")
    return {"id": str(incident.id), "status": incident.status}


# ---------------------------------------------------------------------------
# Control assessments (Annex A / SoA)
# ---------------------------------------------------------------------------

@router.post("/controls/seed")
async def seed_controls(db: AsyncSession = Depends(get_db)):
    """Seed all 18 ISO 42001 Annex A controls. Safe to re-run (idempotent)."""
    inserted = await svc.seed_controls(db)
    return {"seeded": inserted, "message": f"Inserted {inserted} controls (already-existing skipped)"}


@router.get("/controls")
async def list_controls(
    status: str | None = Query(None),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    controls = await svc.list_controls(db, status, category)
    return [
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


@router.post("/controls/{control_id}")
async def upsert_control(
    control_id: str, body: ControlAssessmentUpsert, db: AsyncSession = Depends(get_db)
):
    data = body.model_dump(exclude_none=True)
    # Resolve control_name from registry if not provided
    from app.models.iso_audit import ISO_42001_CONTROLS
    if "control_name" not in data:
        data["control_name"] = ISO_42001_CONTROLS.get(control_id, control_id)
    control = await svc.upsert_control(db, control_id, data)
    return {"control_id": control.control_id, "status": control.status}


# ---------------------------------------------------------------------------
# Audit report
# ---------------------------------------------------------------------------

@router.get("/report")
async def get_audit_report(
    product_id: str | None = Query(None, description="Filter to specific product, or omit for factory-wide"),
    db: AsyncSession = Depends(get_db),
):
    """Generate full ISO 42001 audit readiness report as JSON."""
    report = await svc.generate_audit_report(db, product_id)
    return report


@router.post("/report/publish")
async def publish_audit_report_to_confluence(
    product_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Generate audit report and publish to Confluence. Returns Confluence page ID."""
    report = await svc.generate_audit_report(db, product_id)

    try:
        from app.services.confluence_client import ConfluenceClient
        client = ConfluenceClient()
        parent_title = os.getenv("CONFLUENCE_PARENT_PAGE_TITLE", "ProjectZero Products")
        page_id = await client.publish_iso_audit_report(
            report=report,
            parent_title=parent_title,
            product_id=product_id,
        )
        return {
            "published": True,
            "confluence_page_id": page_id,
            "audit_readiness": report["executive_summary"]["audit_readiness"],
            "compliance_pct": report["executive_summary"]["overall_compliance_pct"],
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Confluence not configured: {exc}")
    except Exception as exc:
        logger.error("Confluence publish failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
