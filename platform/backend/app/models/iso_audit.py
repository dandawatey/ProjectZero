"""ISO/IEC 42001:2023 AI Management System — audit control models.

Implements controls from ISO 42001 Annex A and core clauses:
  - Clause 6 / 8: AI risk register (per workflow / product)
  - Clause 9.1 / A.9.3: AI transparency log (per agent action)
  - Clause 10 / A.10.1: AI incident register
  - Annex A: Control self-assessment registry (A.2–A.10)

Risk levels align with EU AI Act tiers:
  PROHIBITED | HIGH | LIMITED | MINIMAL

Human oversight levels (A.8.3):
  FULL_AUTO | HUMAN_IN_LOOP | HUMAN_ON_LOOP | HUMAN_IN_COMMAND
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float,
    ForeignKey, Index, Integer, JSON, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


# ---------------------------------------------------------------------------
# ISO 42001 Annex A — control IDs reference
# A.2 Policies | A.3 Internal audit | A.4 Stakeholders | A.5 AI system inventory
# A.6 Risk treatment | A.7 Data governance | A.8 Human oversight
# A.9 Transparency | A.10 Accountability | A.11 Third-party AI
# ---------------------------------------------------------------------------

ISO_42001_CONTROLS = {
    "A.2.2": "Policies for AI management",
    "A.2.4": "AI-related roles and responsibilities",
    "A.3.2": "Internal audit procedures",
    "A.4.2": "Stakeholder engagement and communication",
    "A.5.2": "AI system inventory and documentation",
    "A.6.1": "AI risk identification and treatment",
    "A.6.2": "Documentation of AI system purpose and limitations",
    "A.7.2": "Data acquisition, preparation and quality",
    "A.7.4": "Data privacy and protection",
    "A.8.2": "Human oversight mechanisms",
    "A.8.3": "Human review of AI outputs",
    "A.8.4": "Override and intervention capabilities",
    "A.9.3": "AI transparency and explainability",
    "A.9.4": "Communication to affected parties",
    "A.10.1": "Accountability assignment for AI systems",
    "A.10.2": "AI incident response and reporting",
    "A.11.1": "Third-party AI supplier assessment",
    "A.11.2": "Third-party model governance",
}


class AiRiskEntry(Base):
    """ISO 42001 Clause 8.3/8.4 — AI system risk register.

    One entry per workflow run (or product) capturing the risk classification,
    data used, human oversight level, and accountability owner.
    """
    __tablename__ = "ai_risk_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Scope
    product_id = Column(String(255), nullable=True, index=True)
    workflow_run_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    workflow_type = Column(String(100), nullable=True)

    # Risk classification (EU AI Act tiers)
    risk_level = Column(String(20), nullable=False, index=True)
    # PROHIBITED | HIGH | LIMITED | MINIMAL

    # AI system description
    use_case = Column(String(500), nullable=False)
    intended_purpose = Column(Text, nullable=True)
    known_limitations = Column(Text, nullable=True)

    # Data governance (A.7)
    data_inputs = Column(JSON, nullable=True)          # list of data source descriptors
    personal_data_involved = Column(Boolean, default=False)
    sensitive_data_categories = Column(JSON, nullable=True)  # list of categories

    # Human oversight (A.8.2 / A.8.3)
    human_oversight_level = Column(String(30), nullable=False, default="HUMAN_ON_LOOP")
    # FULL_AUTO | HUMAN_IN_LOOP | HUMAN_ON_LOOP | HUMAN_IN_COMMAND

    # Accountability (A.10.1)
    accountability_owner = Column(String(255), nullable=True)
    review_frequency_days = Column(Integer, default=90)
    next_review_at = Column(DateTime(timezone=True), nullable=True)

    # Model transparency (A.9.3)
    ai_model = Column(String(200), nullable=True)        # e.g. claude-sonnet-4-6
    ai_provider = Column(String(100), nullable=True)     # Anthropic / OpenAI / etc.
    model_version = Column(String(100), nullable=True)
    is_third_party_model = Column(Boolean, default=True)

    # Risk treatment
    residual_risk = Column(String(20), nullable=True)    # ACCEPTED | MITIGATED | TRANSFERRED | AVOIDED
    mitigation_notes = Column(Text, nullable=True)
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_risk_product_level", "product_id", "risk_level"),
    )


class AiTransparencyLog(Base):
    """ISO 42001 A.9.3 — per-agent-action transparency log.

    Every agent action generates one entry recording: model, decision type,
    whether human review was required, whether the outcome was accepted,
    and the reasoning provided.
    """
    __tablename__ = "ai_transparency_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Link to execution context
    workflow_run_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    agent_contribution_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    correlation_id = Column(String(255), nullable=True, index=True)

    # Agent identity
    agent_id = Column(String(200), nullable=False, index=True)
    agent_type = Column(String(100), nullable=False)
    stage = Column(String(100), nullable=True)

    # Model used (A.9.3 — explainability)
    ai_model = Column(String(200), nullable=True)
    ai_provider = Column(String(100), nullable=True)

    # Decision classification
    decision_type = Column(String(100), nullable=False)
    # CODE_GENERATION | ARCHITECTURE_DECISION | TEST_GENERATION |
    # REQUIREMENT_EXTRACTION | REVIEW_JUDGEMENT | APPROVAL_RECOMMENDATION |
    # RISK_ASSESSMENT | DATA_TRANSFORMATION | CONTENT_GENERATION

    # Prompt category (without storing actual prompts — privacy)
    prompt_category = Column(String(100), nullable=True)
    # SPECIFICATION | IMPLEMENTATION | REVIEW | ANALYSIS | SUMMARISATION

    # Human oversight evidence (A.8.3)
    human_review_required = Column(Boolean, default=False)
    human_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Outcome traceability
    outcome_accepted = Column(Boolean, nullable=True)   # None = not yet reviewed
    rejection_reason = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)     # 0-1 if provided by model

    # Explanation / reasoning snippet (no full prompt — just summary)
    reasoning_summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_transparency_agent_type", "agent_type", "decision_type"),
        Index("ix_transparency_workflow", "workflow_run_id", "created_at"),
    )


class AiIncident(Base):
    """ISO 42001 A.10.2 / Clause 10 — AI incident register.

    Records any incident where AI output caused unintended harm, deviation,
    or required escalation. Maps to ISO 42001 nonconformity and corrective action.
    """
    __tablename__ = "ai_incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Classification
    incident_type = Column(String(100), nullable=False, index=True)
    # HALLUCINATION | BIAS_DETECTED | SECURITY_BREACH | PRIVACY_VIOLATION |
    # INCORRECT_OUTPUT | GOVERNANCE_BYPASS | UNAPPROVED_ACTION | SYSTEM_FAILURE

    severity = Column(String(20), nullable=False, index=True)
    # CRITICAL | HIGH | MEDIUM | LOW

    # Context
    product_id = Column(String(255), nullable=True, index=True)
    workflow_run_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    agent_id = Column(String(200), nullable=True)
    stage = Column(String(100), nullable=True)

    # Description
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    ai_involvement = Column(Text, nullable=True)        # how AI contributed to incident
    immediate_impact = Column(Text, nullable=True)

    # Corrective action (ISO 10.1 / 10.2)
    status = Column(String(50), nullable=False, default="open", index=True)
    # open | investigating | remediated | closed | false_positive

    root_cause = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    preventive_action = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True)

    # Accountability
    reported_by = Column(String(255), nullable=True)
    assigned_to = Column(String(255), nullable=True)
    resolved_by = Column(String(255), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Regulatory notification required?
    requires_regulatory_notification = Column(Boolean, default=False)
    regulatory_notified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AiControlAssessment(Base):
    """ISO 42001 Annex A — control self-assessment registry.

    One row per ISO 42001 Annex A control. Records compliance status,
    evidence pointers, gaps, and remediation plans. Used to generate
    Statement of Applicability (SoA) and audit readiness report.
    """
    __tablename__ = "ai_control_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Control identity
    control_id = Column(String(20), nullable=False, unique=True, index=True)
    # e.g. "A.8.3"
    control_name = Column(String(500), nullable=False)
    control_clause = Column(String(20), nullable=True)  # e.g. "A.8"
    control_category = Column(String(100), nullable=True)
    # GOVERNANCE | RISK | DATA | OVERSIGHT | TRANSPARENCY | ACCOUNTABILITY | THIRD_PARTY

    # Applicability
    is_applicable = Column(Boolean, default=True)
    exclusion_justification = Column(Text, nullable=True)

    # Compliance status
    status = Column(String(30), nullable=False, default="not_assessed", index=True)
    # COMPLIANT | PARTIAL | NON_COMPLIANT | NOT_ASSESSED | NOT_APPLICABLE

    compliance_score = Column(Integer, nullable=True)   # 0–100

    # Evidence
    evidence = Column(JSON, nullable=True)              # list of evidence descriptors
    # e.g. [{"type": "workflow_gate", "ref": "MCRA approval at review stage"}]
    evidence_links = Column(JSON, nullable=True)        # confluence/jira URLs

    # Gap analysis
    gap_description = Column(Text, nullable=True)
    risk_if_unaddressed = Column(String(20), nullable=True)  # HIGH | MEDIUM | LOW

    # Remediation
    remediation_plan = Column(Text, nullable=True)
    remediation_owner = Column(String(255), nullable=True)
    remediation_due = Column(DateTime(timezone=True), nullable=True)
    remediation_status = Column(String(30), nullable=True)
    # NOT_STARTED | IN_PROGRESS | COMPLETED | DEFERRED

    # Audit trail
    last_assessed_by = Column(String(255), nullable=True)
    last_assessed_at = Column(DateTime(timezone=True), nullable=True)
    next_assessment_due = Column(DateTime(timezone=True), nullable=True)
    assessment_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
