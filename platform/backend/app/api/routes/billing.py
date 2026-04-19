"""Billing API routes — SaaS-BILL-2.

POST /api/v1/billing/checkout-session — create Stripe checkout
GET /api/v1/billing/subscription — current subscription
POST /api/v1/billing/cancel-subscription — cancel subscription
POST /api/v1/billing/update-payment-method — update payment method
POST /api/v1/billing/webhook — Stripe webhook handler
GET /api/v1/billing/tiers — pricing tiers info
"""

from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth_deps import get_current_user
from app.models.user import User
from app.schemas.billing import (
    CheckoutSessionRequest, CheckoutSessionResponse, SubscriptionRead,
    CancelSubscriptionRequest, CancelSubscriptionResponse,
    PaymentMethodRequest, PaymentMethodResponse, WebhookEvent, WebhookResponse,
    TierInfo
)
from app.services import billing_service as svc

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


@router.post(
    "/checkout-session",
    response_model=CheckoutSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def create_checkout_session(
    req: CheckoutSessionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create Stripe checkout session for subscription."""
    return await svc.create_checkout_session(db, user, req)


@router.get(
    "/subscription",
    response_model=SubscriptionRead | None,
    status_code=status.HTTP_200_OK,
)
async def get_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription for user."""
    return await svc.get_subscription(db, user)


@router.post(
    "/cancel-subscription",
    response_model=CancelSubscriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_subscription(
    req: CancelSubscriptionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel user's subscription."""
    return await svc.cancel_subscription(db, user, req.reason)


@router.post(
    "/update-payment-method",
    response_model=PaymentMethodResponse,
    status_code=status.HTTP_200_OK,
)
async def update_payment_method(
    req: PaymentMethodRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update payment method for subscription."""
    return await svc.update_payment_method(db, user, req.stripe_payment_method_id)


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
)
async def webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Stripe webhook handler."""
    # Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature or not svc.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Parse event
    event = await request.json()
    event_id = event.get("id")

    # Process event
    await svc.process_webhook(db, event)

    return WebhookResponse(received=True, event_id=event_id)


@router.get(
    "/tiers",
    response_model=list[TierInfo],
    status_code=status.HTTP_200_OK,
)
async def get_pricing_tiers():
    """Get available pricing tiers (public endpoint)."""
    return svc.get_tier_pricing()
