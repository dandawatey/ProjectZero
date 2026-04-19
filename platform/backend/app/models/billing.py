"""Billing + Subscription models — SaaS-BILL-2."""

import uuid

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Import User to ensure SQLAlchemy mapper can resolve "User" relationship
# Must be after Base import to avoid circular deps
from app.models.user import User  # noqa: F401


class BillingSubscription(Base):
    """User subscription to tiered plan."""
    __tablename__ = "billing_subscriptions"
    __table_args__ = (
        CheckConstraint(
            "tier IN ('starter','professional','enterprise')",
            name="ck_subscription_tier"
        ),
        CheckConstraint(
            "status IN ('active','cancelled','suspended','past_due')",
            name="ck_subscription_status"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # For RLS + multi-tenant
    tier = Column(String(20), nullable=False, default="starter")  # starter|professional|enterprise
    status = Column(String(20), nullable=False, default="active")  # active|cancelled|suspended|past_due
    stripe_customer_id = Column(String(255), nullable=False, unique=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)  # null before first charge
    stripe_payment_method_id = Column(String(255), nullable=True)  # Stripe PM ID

    # Pricing: in cents (USD)
    price_per_month = Column(Integer, nullable=False)  # 2900 (starter), 9900 (prof), 0 (custom)

    # Billing cycle
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    renewal_date = Column(DateTime(timezone=True), nullable=True)

    # Cancellation (soft delete)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(500), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class BillingInvoice(Base):
    """Invoice for subscription charge."""
    __tablename__ = "billing_invoices"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','sent','paid','failed','refunded')",
            name="ck_invoice_status"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("billing_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_invoice_id = Column(String(255), nullable=False, unique=True, index=True)

    amount_cents = Column(Integer, nullable=False)  # in cents
    status = Column(String(20), nullable=False, default="draft")
    paid_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    subscription = relationship("BillingSubscription", foreign_keys=[subscription_id])


class BillingWebhookEvent(Base):
    """Log of received Stripe webhook events."""
    __tablename__ = "billing_webhook_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stripe_event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # customer.subscription.updated, etc.
    processed = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
