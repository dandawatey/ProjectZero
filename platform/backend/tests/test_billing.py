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
