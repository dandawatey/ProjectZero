"""Billing service — Stripe integration — SaaS-BILL-2."""

import os
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.billing import BillingSubscription, BillingInvoice, BillingWebhookEvent
from app.models.user import User
from app.schemas.billing import (
    CheckoutSessionRequest, CheckoutSessionResponse, SubscriptionRead,
    CancelSubscriptionResponse, PaymentMethodResponse, TierInfo
)


# Stripe tiers: price in cents
TIER_PRICING = {
    "starter": {"price": 2900, "description": "For individuals", "features": ["Basic features"]},
    "professional": {"price": 9900, "description": "For teams", "features": ["Advanced features"]},
    "enterprise": {"price": 0, "description": "Custom pricing", "features": ["All features", "Dedicated support"]},
}


def _get_stripe_key() -> str:
    """Get Stripe API key from config."""
    key = os.getenv("STRIPE_API_KEY")
    if not key:
        raise ValueError("STRIPE_API_KEY not configured")
    return key


def _get_webhook_secret() -> str:
    """Get Stripe webhook secret from config."""
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise ValueError("STRIPE_WEBHOOK_SECRET not configured")
    return secret


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature."""
    secret = _get_webhook_secret()
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


async def create_checkout_session(
    db: AsyncSession,
    user: User,
    req: CheckoutSessionRequest,
) -> CheckoutSessionResponse:
    """Create Stripe checkout session for subscription."""
    if req.tier not in TIER_PRICING:
        raise ValueError(f"Invalid tier: {req.tier}")

    stripe.api_key = _get_stripe_key()

    # Get or create Stripe customer
    result = await db.execute(
        select(BillingSubscription).where(BillingSubscription.user_id == user.id)
    )
    existing_sub = result.scalars().first()

    if existing_sub and existing_sub.stripe_customer_id:
        stripe_customer_id = existing_sub.stripe_customer_id
    else:
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"user_id": str(user.id)},
        )
        stripe_customer_id = customer.id

    # Create checkout session
    pricing = TIER_PRICING[req.tier]
    session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"{req.tier.title()} Plan"},
                    "unit_amount": pricing["price"],
                    "recurring": {"interval": "month", "interval_count": 1},
                },
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=f"{req.return_url}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=req.return_url,
        metadata={"tier": req.tier, "user_id": str(user.id)},
    )

    # Store in DB
    if not existing_sub:
        sub = BillingSubscription(
            user_id=user.id,
            org_id=user.id,  # TODO: get from user.org_id when available
            tier=req.tier,
            stripe_customer_id=stripe_customer_id,
            price_per_month=pricing["price"],
            status="active",
        )
        db.add(sub)
        await db.commit()

    return CheckoutSessionResponse(
        session_id=session.id,
        checkout_url=session.url,
        expires_at=datetime.fromtimestamp(session.expires_at),
    )


async def get_subscription(
    db: AsyncSession,
    user: User,
) -> Optional[SubscriptionRead]:
    """Get current subscription for user."""
    result = await db.execute(
        select(BillingSubscription).where(
            BillingSubscription.user_id == user.id,
            BillingSubscription.cancelled_at == None,
        )
    )
    sub = result.scalars().first()
    if not sub:
        return None

    return SubscriptionRead(
        id=str(sub.id),
        tier=sub.tier,
        status=sub.status,
        renewal_date=sub.renewal_date,
        current_period_end=sub.current_period_end,
        price_per_month=sub.price_per_month,
        stripe_subscription_id=sub.stripe_subscription_id,
    )


async def cancel_subscription(
    db: AsyncSession,
    user: User,
    reason: str,
) -> CancelSubscriptionResponse:
    """Cancel subscription (soft delete)."""
    result = await db.execute(
        select(BillingSubscription).where(BillingSubscription.user_id == user.id)
    )
    sub = result.scalars().first()
    if not sub:
        raise ValueError("No subscription found")

    stripe.api_key = _get_stripe_key()
    if sub.stripe_subscription_id:
        stripe.Subscription.delete(sub.stripe_subscription_id)

    sub.status = "cancelled"
    sub.cancelled_at = datetime.utcnow()
    sub.cancellation_reason = reason
    await db.commit()

    return CancelSubscriptionResponse(
        id=str(sub.id),
        status=sub.status,
        cancelled_at=sub.cancelled_at,
    )


async def update_payment_method(
    db: AsyncSession,
    user: User,
    stripe_payment_method_id: str,
) -> PaymentMethodResponse:
    """Update Stripe payment method."""
    result = await db.execute(
        select(BillingSubscription).where(BillingSubscription.user_id == user.id)
    )
    sub = result.scalars().first()
    if not sub:
        raise ValueError("No subscription found")

    stripe.api_key = _get_stripe_key()

    # Attach payment method to customer
    pm = stripe.PaymentMethod.retrieve(stripe_payment_method_id)
    pm.attach(customer=sub.stripe_customer_id)

    # Update subscription default payment method
    if sub.stripe_subscription_id:
        stripe.Subscription.modify(
            sub.stripe_subscription_id,
            default_payment_method=stripe_payment_method_id,
        )

    sub.stripe_payment_method_id = stripe_payment_method_id
    await db.commit()

    return PaymentMethodResponse(
        payment_method_id=stripe_payment_method_id,
        last_four=pm.get("card", {}).get("last4"),
        card_brand=pm.get("card", {}).get("brand"),
    )


async def process_webhook(
    db: AsyncSession,
    event: dict,
) -> bool:
    """Process Stripe webhook event."""
    event_id = event.get("id")
    event_type = event.get("type")

    # Deduplicate
    result = await db.execute(
        select(BillingWebhookEvent).where(BillingWebhookEvent.stripe_event_id == event_id)
    )
    if result.scalars().first():
        return True  # Already processed

    # Log event
    webhook = BillingWebhookEvent(
        stripe_event_id=event_id,
        event_type=event_type,
    )
    db.add(webhook)

    # Handle event types
    if event_type == "customer.subscription.updated":
        await _handle_subscription_updated(db, event)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(db, event)
    elif event_type == "invoice.paid":
        await _handle_invoice_paid(db, event)
    elif event_type == "invoice.payment_failed":
        await _handle_invoice_failed(db, event)

    webhook.processed = True
    await db.commit()
    return True


async def _handle_subscription_updated(db: AsyncSession, event: dict) -> None:
    """Handle customer.subscription.updated."""
    sub_data = event.get("data", {}).get("object", {})
    stripe_sub_id = sub_data.get("id")

    result = await db.execute(
        select(BillingSubscription).where(
            BillingSubscription.stripe_subscription_id == stripe_sub_id
        )
    )
    sub = result.scalars().first()
    if not sub:
        return

    # Update from Stripe
    sub.status = sub_data.get("status", "active")
    sub.current_period_start = datetime.fromtimestamp(sub_data.get("current_period_start"))
    sub.current_period_end = datetime.fromtimestamp(sub_data.get("current_period_end"))
    sub.renewal_date = sub.current_period_end


async def _handle_subscription_deleted(db: AsyncSession, event: dict) -> None:
    """Handle customer.subscription.deleted."""
    sub_data = event.get("data", {}).get("object", {})
    stripe_sub_id = sub_data.get("id")

    result = await db.execute(
        select(BillingSubscription).where(
            BillingSubscription.stripe_subscription_id == stripe_sub_id
        )
    )
    sub = result.scalars().first()
    if sub:
        sub.status = "cancelled"
        sub.cancelled_at = datetime.utcnow()


async def _handle_invoice_paid(db: AsyncSession, event: dict) -> None:
    """Handle invoice.paid."""
    invoice_data = event.get("data", {}).get("object", {})
    stripe_invoice_id = invoice_data.get("id")

    result = await db.execute(
        select(BillingInvoice).where(BillingInvoice.stripe_invoice_id == stripe_invoice_id)
    )
    invoice = result.scalars().first()
    if invoice:
        invoice.status = "paid"
        invoice.paid_at = datetime.utcnow()


async def _handle_invoice_failed(db: AsyncSession, event: dict) -> None:
    """Handle invoice.payment_failed."""
    invoice_data = event.get("data", {}).get("object", {})
    stripe_invoice_id = invoice_data.get("id")

    result = await db.execute(
        select(BillingInvoice).where(BillingInvoice.stripe_invoice_id == stripe_invoice_id)
    )
    invoice = result.scalars().first()
    if invoice:
        invoice.status = "failed"

    # Update subscription status
    stripe_sub_id = invoice_data.get("subscription")
    result = await db.execute(
        select(BillingSubscription).where(
            BillingSubscription.stripe_subscription_id == stripe_sub_id
        )
    )
    sub = result.scalars().first()
    if sub:
        sub.status = "past_due"


def get_tier_pricing() -> list[TierInfo]:
    """Get available pricing tiers."""
    return [
        TierInfo(
            name="starter",
            description=TIER_PRICING["starter"]["description"],
            price=TIER_PRICING["starter"]["price"],
            features=TIER_PRICING["starter"]["features"],
        ),
        TierInfo(
            name="professional",
            description=TIER_PRICING["professional"]["description"],
            price=TIER_PRICING["professional"]["price"],
            features=TIER_PRICING["professional"]["features"],
        ),
        TierInfo(
            name="enterprise",
            description=TIER_PRICING["enterprise"]["description"],
            price=None,  # Custom pricing
            features=TIER_PRICING["enterprise"]["features"],
        ),
    ]
