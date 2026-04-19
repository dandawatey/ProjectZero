"""Billing API tests — SaaS-BILL-2.

POST /api/v1/billing/checkout-session — create Stripe checkout
GET /api/v1/billing/subscription — get current subscription + renewal date
POST /api/v1/billing/cancel-subscription — cancel subscription (soft delete)
POST /api/v1/billing/update-payment-method — update Stripe payment method
POST /api/v1/billing/webhook — Stripe webhook handler
RLS: Users access only own org subscription
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_checkout_no_auth(client):
    """POST /api/v1/billing/checkout-session without auth → 401."""
    r = await client.post(
        "/api/v1/billing/checkout-session",
        json={"tier": "professional", "return_url": "http://localhost:3000"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tier_pricing_tiers_exist(client):
    """Verify pricing tiers: Starter=$29/mo, Professional=$99/mo, Enterprise=custom."""
    r = await client.get("/api/v1/billing/tiers")
    assert r.status_code == 200
    data = r.json()
    tiers = {t["name"]: t for t in data}
    assert "starter" in tiers
    assert "professional" in tiers
    assert "enterprise" in tiers
    assert tiers["starter"]["price"] == 2900  # cents
    assert tiers["professional"]["price"] == 9900
    assert tiers["enterprise"]["price"] is None  # custom


@pytest.mark.asyncio
async def test_webhook_signature_invalid(client):
    """POST /api/v1/billing/webhook with invalid signature → 401."""
    import os
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"

    event = {"id": "evt_test_1234", "type": "customer.subscription.updated"}
    r = await client.post(
        "/api/v1/billing/webhook",
        json=event,
        headers={"stripe-signature": "test_sig_invalid"}
    )
    assert r.status_code == 401


# Service layer tests (mocked Stripe)
@pytest.mark.asyncio
async def test_billing_subscription_model():
    """Test BillingSubscription model attributes."""
    from app.models.billing import BillingSubscription
    import uuid

    sub = BillingSubscription(
        user_id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        tier="professional",
        stripe_customer_id="cus_test_1234",
        price_per_month=9900,
        status="active",
    )
    assert sub.tier == "professional"
    assert sub.price_per_month == 9900
    assert sub.status == "active"


@pytest.mark.asyncio
async def test_billing_invoice_model():
    """Test BillingInvoice model."""
    from app.models.billing import BillingInvoice, BillingSubscription
    import uuid

    sub = BillingSubscription(
        user_id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        tier="starter",
        stripe_customer_id="cus_test",
        price_per_month=2900,
    )
    inv = BillingInvoice(
        subscription_id=sub.id,
        stripe_invoice_id="in_test_1234",
        amount_cents=2900,
        status="sent",
    )
    assert inv.status == "sent"
    assert inv.amount_cents == 2900


@pytest.mark.asyncio
async def test_get_tier_pricing():
    """Test tier pricing list."""
    from app.services import billing_service as svc

    tiers = svc.get_tier_pricing()
    assert len(tiers) == 3
    assert tiers[0].price == 2900
    assert tiers[1].price == 9900
    assert tiers[2].price is None  # enterprise


@pytest.mark.asyncio
async def test_verify_webhook_signature():
    """Test webhook signature verification."""
    from app.services.billing_service import verify_webhook_signature
    import os
    import hmac
    import hashlib

    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_secret"
    payload = b"test_payload"
    secret = "test_secret"

    # Generate valid signature
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(payload, expected) is True

    # Invalid signature
    assert verify_webhook_signature(payload, "invalid_sig") is False
