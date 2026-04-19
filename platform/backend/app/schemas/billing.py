"""Billing schemas — SaaS-BILL-2."""

from datetime import datetime
from pydantic import BaseModel, Field


class CheckoutSessionRequest(BaseModel):
    """POST /api/v1/billing/checkout-session request."""
    tier: str = Field(..., description="starter|professional|enterprise")
    return_url: str = Field(..., description="URL to redirect after checkout")


class CheckoutSessionResponse(BaseModel):
    """Checkout session response with Stripe redirect URL."""
    session_id: str
    checkout_url: str
    expires_at: datetime


class SubscriptionRead(BaseModel):
    """GET /api/v1/billing/subscription response."""
    id: str
    tier: str
    status: str  # active|cancelled|suspended|past_due
    renewal_date: datetime
    current_period_end: datetime
    price_per_month: int  # cents
    stripe_subscription_id: str | None = None

    class Config:
        from_attributes = True


class CancelSubscriptionRequest(BaseModel):
    """POST /api/v1/billing/cancel-subscription request."""
    reason: str = Field(default="user requested", description="Reason for cancellation")


class CancelSubscriptionResponse(BaseModel):
    """Cancellation response."""
    id: str
    status: str
    cancelled_at: datetime


class PaymentMethodRequest(BaseModel):
    """POST /api/v1/billing/update-payment-method request."""
    stripe_payment_method_id: str = Field(..., description="Stripe payment method ID (pm_*)")


class PaymentMethodResponse(BaseModel):
    """Payment method updated response."""
    payment_method_id: str
    last_four: str | None = None
    card_brand: str | None = None


class TierInfo(BaseModel):
    """Pricing tier info."""
    name: str
    description: str
    price: int | None  # cents, None for enterprise (custom)
    features: list[str]


class WebhookEvent(BaseModel):
    """Stripe webhook event payload."""
    id: str
    type: str
    data: dict


class WebhookResponse(BaseModel):
    """Webhook processing response."""
    received: bool
    event_id: str
