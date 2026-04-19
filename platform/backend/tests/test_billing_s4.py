"""SaaS-BILL-2.0-S4 — Stripe Checkout + Webhook Handler — TDD tests.

Endpoints tested:
  POST /api/v1/billing/checkout-session
  POST /api/v1/billing/webhook
  GET  /api/v1/billing/subscription
  POST /api/v1/billing/cancel-subscription

Service functions tested:
  create_checkout_session()
  process_webhook()
  get_subscription()
  cancel_subscription()
"""

import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_db_mock(first_result=None, *, side_effect_sequence: list | None = None):
    """Return AsyncMock db with execute().scalars().first() configured.

    Correct AsyncMock pattern:
        1. Create mock_result = MagicMock()
        2. Set mock_result.scalars().first() return value
        3. Pass as return_value to AsyncMock(execute)

    side_effect_sequence: list of values for successive execute() calls.
    """
    db = AsyncMock()

    if side_effect_sequence is not None:
        results = []
        for r in side_effect_sequence:
            mock_result = MagicMock()
            mock_result.scalars.return_value.first.return_value = r
            results.append(mock_result)
        db.execute = AsyncMock(side_effect=results)
    else:
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = first_result
        db.execute = AsyncMock(return_value=mock_result)

    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


def _make_user(email="admin@example.com", org_id=None):
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = email
    user.org_id = org_id or uuid.uuid4()
    return user


def _stripe_sig(payload: bytes, secret: str = "whsec_test") -> str:
    """Generate HMAC-SHA256 sig matching billing_service.verify_webhook_signature."""
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# 1. create_checkout_session
# ---------------------------------------------------------------------------

class TestCreateCheckoutSession:
    """Tests for svc.create_checkout_session()."""

    @pytest.mark.asyncio
    async def test_checkout_valid_new_customer(self):
        """Valid tier for new customer → creates Stripe customer + session, returns url."""
        from app.services import billing_service as svc
        from app.schemas.billing import CheckoutSessionRequest

        db = _make_db_mock(first_result=None)  # no existing subscription
        user = _make_user()
        req = CheckoutSessionRequest(tier="professional", return_url="https://app.test/billing")

        mock_customer = MagicMock()
        mock_customer.id = "cus_test123"

        mock_session = MagicMock()
        mock_session.id = "cs_test456"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test456"
        mock_session.expires_at = int((datetime.utcnow() + timedelta(hours=1)).timestamp())

        with patch.dict(os.environ, {"STRIPE_API_KEY": "sk_test_fake", "STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            with patch("app.services.billing_service.stripe") as mock_stripe:
                mock_stripe.Customer.create.return_value = mock_customer
                mock_stripe.checkout.Session.create.return_value = mock_session

                resp = await svc.create_checkout_session(db, user, req)

        assert resp.session_id == "cs_test456"
        assert resp.checkout_url == "https://checkout.stripe.com/pay/cs_test456"
        mock_stripe.Customer.create.assert_called_once()
        mock_stripe.checkout.Session.create.assert_called_once()
        db.add.assert_called_once()
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_checkout_valid_existing_customer(self):
        """Existing subscription → reuses stripe_customer_id, no new customer created."""
        from app.services import billing_service as svc
        from app.schemas.billing import CheckoutSessionRequest
        from app.models.billing import BillingSubscription

        existing_sub = MagicMock(spec=BillingSubscription)
        existing_sub.stripe_customer_id = "cus_existing789"

        db = _make_db_mock(first_result=existing_sub)
        user = _make_user()
        req = CheckoutSessionRequest(tier="professional", return_url="https://app.test/billing")

        mock_session = MagicMock()
        mock_session.id = "cs_existing999"
        mock_session.url = "https://checkout.stripe.com/pay/cs_existing999"
        mock_session.expires_at = int((datetime.utcnow() + timedelta(hours=1)).timestamp())

        with patch.dict(os.environ, {"STRIPE_API_KEY": "sk_test_fake", "STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            with patch("app.services.billing_service.stripe") as mock_stripe:
                mock_stripe.checkout.Session.create.return_value = mock_session

                resp = await svc.create_checkout_session(db, user, req)

        assert resp.session_id == "cs_existing999"
        mock_stripe.Customer.create.assert_not_called()  # reused existing
        db.add.assert_not_called()  # no new sub record

    @pytest.mark.asyncio
    async def test_checkout_invalid_tier_raises(self):
        """Invalid tier → ValueError before Stripe call."""
        from app.services import billing_service as svc
        from app.schemas.billing import CheckoutSessionRequest

        db = _make_db_mock()
        user = _make_user()
        req = CheckoutSessionRequest(tier="ultra_premium", return_url="https://app.test")

        with patch.dict(os.environ, {"STRIPE_API_KEY": "sk_test_fake", "STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            with pytest.raises(ValueError, match="Invalid tier"):
                await svc.create_checkout_session(db, user, req)

    @pytest.mark.asyncio
    async def test_checkout_professional_pricing(self):
        """Professional tier → $99/mo (9900 cents)."""
        from app.services import billing_service as svc
        from app.schemas.billing import CheckoutSessionRequest

        db = _make_db_mock(first_result=None)
        user = _make_user()
        req = CheckoutSessionRequest(tier="professional", return_url="https://app.test")

        mock_customer = MagicMock()
        mock_customer.id = "cus_prof"
        mock_session = MagicMock()
        mock_session.id = "cs_prof"
        mock_session.url = "https://checkout.stripe.com/pay/cs_prof"
        mock_session.expires_at = int((datetime.utcnow() + timedelta(hours=1)).timestamp())

        with patch.dict(os.environ, {"STRIPE_API_KEY": "sk_test_fake", "STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            with patch("app.services.billing_service.stripe") as mock_stripe:
                mock_stripe.Customer.create.return_value = mock_customer
                mock_stripe.checkout.Session.create.return_value = mock_session

                await svc.create_checkout_session(db, user, req)

        # Verify line_items has professional pricing (9900 cents)
        call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
        unit_amount = call_kwargs["line_items"][0]["price_data"]["unit_amount"]
        assert unit_amount == 9900

    @pytest.mark.asyncio
    async def test_checkout_missing_stripe_key_raises(self):
        """Missing STRIPE_API_KEY → ValueError."""
        from app.services import billing_service as svc
        from app.schemas.billing import CheckoutSessionRequest

        db = _make_db_mock(first_result=None)
        user = _make_user()
        req = CheckoutSessionRequest(tier="starter", return_url="https://app.test")

        env = {"STRIPE_WEBHOOK_SECRET": "whsec_test"}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("STRIPE_API_KEY", None)
            with pytest.raises(ValueError, match="STRIPE_API_KEY"):
                await svc.create_checkout_session(db, user, req)


# ---------------------------------------------------------------------------
# 2. process_webhook
# ---------------------------------------------------------------------------

class TestProcessWebhook:
    """Tests for svc.process_webhook()."""

    def _make_subscription_updated_event(self, stripe_sub_id: str = "sub_test") -> dict:
        return {
            "id": "evt_001",
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": stripe_sub_id,
                    "status": "active",
                    "current_period_start": int(datetime.utcnow().timestamp()),
                    "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
                }
            }
        }

    def _make_subscription_deleted_event(self, stripe_sub_id: str = "sub_test") -> dict:
        return {
            "id": "evt_002",
            "type": "customer.subscription.deleted",
            "data": {"object": {"id": stripe_sub_id}}
        }

    def _make_invoice_paid_event(self, invoice_id: str = "inv_001") -> dict:
        return {
            "id": "evt_003",
            "type": "invoice.paid",
            "data": {"object": {"id": invoice_id, "subscription": "sub_test"}}
        }

    def _make_invoice_failed_event(self, invoice_id: str = "inv_002") -> dict:
        return {
            "id": "evt_004",
            "type": "invoice.payment_failed",
            "data": {"object": {"id": invoice_id, "subscription": "sub_test"}}
        }

    @pytest.mark.asyncio
    async def test_webhook_valid_signature_accepted(self):
        """Valid HMAC sig → verify_webhook_signature returns True."""
        from app.services.billing_service import verify_webhook_signature

        payload = b'{"id": "evt_001", "type": "test"}'
        secret = "whsec_test_secret"
        sig = _stripe_sig(payload, secret)

        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": secret}):
            assert verify_webhook_signature(payload, sig) is True

    @pytest.mark.asyncio
    async def test_webhook_invalid_signature_rejected(self):
        """Tampered sig → verify_webhook_signature returns False."""
        from app.services.billing_service import verify_webhook_signature

        payload = b'{"id": "evt_001"}'
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_real"}):
            assert verify_webhook_signature(payload, "bad_signature") is False

    @pytest.mark.asyncio
    async def test_webhook_idempotency_duplicate_skipped(self):
        """Duplicate event_id → returns True without reprocessing."""
        from app.services import billing_service as svc
        from app.models.billing import BillingWebhookEvent

        # First execute() finds existing webhook (idempotency check)
        existing_event = MagicMock(spec=BillingWebhookEvent)
        existing_event.stripe_event_id = "evt_001"
        db = _make_db_mock(first_result=existing_event)

        event = self._make_subscription_updated_event()
        result = await svc.process_webhook(db, event)

        assert result is True
        db.add.assert_not_called()  # no second log added

    @pytest.mark.asyncio
    async def test_webhook_subscription_updated_new_event(self):
        """New customer.subscription.updated → logged + subscription updated."""
        from app.services import billing_service as svc
        from app.models.billing import BillingSubscription

        existing_sub = MagicMock(spec=BillingSubscription)
        existing_sub.stripe_subscription_id = "sub_test"
        existing_sub.status = "active"

        # execute() calls: 1=idempotency(None), 2=find subscription
        db = _make_db_mock(side_effect_sequence=[None, existing_sub])

        event = self._make_subscription_updated_event("sub_test")
        result = await svc.process_webhook(db, event)

        assert result is True
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_webhook_subscription_deleted(self):
        """customer.subscription.deleted → sub status = 'cancelled'."""
        from app.services import billing_service as svc
        from app.models.billing import BillingSubscription

        existing_sub = MagicMock(spec=BillingSubscription)
        existing_sub.status = "active"
        existing_sub.cancelled_at = None

        db = _make_db_mock(side_effect_sequence=[None, existing_sub])

        event = self._make_subscription_deleted_event()
        await svc.process_webhook(db, event)

        assert existing_sub.status == "cancelled"
        assert existing_sub.cancelled_at is not None

    @pytest.mark.asyncio
    async def test_webhook_invoice_paid(self):
        """invoice.paid → invoice.status = 'paid'."""
        from app.services import billing_service as svc
        from app.models.billing import BillingInvoice

        invoice = MagicMock(spec=BillingInvoice)
        invoice.status = "pending"
        invoice.paid_at = None

        db = _make_db_mock(side_effect_sequence=[None, invoice])

        event = self._make_invoice_paid_event("inv_001")
        await svc.process_webhook(db, event)

        assert invoice.status == "paid"
        assert invoice.paid_at is not None

    @pytest.mark.asyncio
    async def test_webhook_invoice_payment_failed(self):
        """invoice.payment_failed → invoice.status = 'failed', sub → 'past_due'."""
        from app.services import billing_service as svc
        from app.models.billing import BillingInvoice, BillingSubscription

        invoice = MagicMock(spec=BillingInvoice)
        invoice.status = "pending"

        sub = MagicMock(spec=BillingSubscription)
        sub.status = "active"

        db = _make_db_mock(side_effect_sequence=[None, invoice, sub])

        event = self._make_invoice_failed_event("inv_002")
        await svc.process_webhook(db, event)

        assert invoice.status == "failed"
        assert sub.status == "past_due"

    @pytest.mark.asyncio
    async def test_webhook_unknown_event_still_logged(self):
        """Unknown event type → logged but no handler error."""
        from app.services import billing_service as svc

        db = _make_db_mock(side_effect_sequence=[None])

        event = {"id": "evt_unknown", "type": "some.unknown.event", "data": {"object": {}}}
        result = await svc.process_webhook(db, event)

        assert result is True
        db.add.assert_called_once()  # still logged
        db.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# 3. get_subscription
# ---------------------------------------------------------------------------

class TestGetSubscription:
    """Tests for svc.get_subscription()."""

    @pytest.mark.asyncio
    async def test_get_subscription_exists(self):
        """Active subscription → returns SubscriptionRead."""
        from app.services import billing_service as svc
        from app.models.billing import BillingSubscription

        sub = MagicMock(spec=BillingSubscription)
        sub.id = uuid.uuid4()
        sub.tier = "professional"
        sub.status = "active"
        sub.renewal_date = datetime.utcnow() + timedelta(days=30)
        sub.current_period_end = sub.renewal_date
        sub.price_per_month = 9900
        sub.stripe_subscription_id = "sub_testXYZ"

        db = _make_db_mock(first_result=sub)
        user = _make_user()

        result = await svc.get_subscription(db, user)

        assert result is not None
        assert result.tier == "professional"
        assert result.status == "active"
        assert result.price_per_month == 9900

    @pytest.mark.asyncio
    async def test_get_subscription_not_found(self):
        """No active subscription → returns None."""
        from app.services import billing_service as svc

        db = _make_db_mock(first_result=None)
        user = _make_user()

        result = await svc.get_subscription(db, user)

        assert result is None


# ---------------------------------------------------------------------------
# 4. cancel_subscription
# ---------------------------------------------------------------------------

class TestCancelSubscription:
    """Tests for svc.cancel_subscription()."""

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self):
        """Active subscription → cancelled in DB, Stripe.Subscription.delete called."""
        from app.services import billing_service as svc
        from app.models.billing import BillingSubscription

        sub = MagicMock(spec=BillingSubscription)
        sub.id = uuid.uuid4()
        sub.status = "active"
        sub.stripe_subscription_id = "sub_tocancel"
        sub.cancelled_at = None

        db = _make_db_mock(first_result=sub)
        user = _make_user()

        with patch.dict(os.environ, {"STRIPE_API_KEY": "sk_test_fake", "STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            with patch("app.services.billing_service.stripe") as mock_stripe:
                resp = await svc.cancel_subscription(db, user, reason="not needed")

        assert resp.status == "cancelled"
        mock_stripe.Subscription.delete.assert_called_once_with("sub_tocancel")
        assert sub.cancelled_at is not None

    @pytest.mark.asyncio
    async def test_cancel_subscription_no_stripe_sub_id(self):
        """Subscription without stripe_subscription_id → no Stripe call, still cancelled."""
        from app.services import billing_service as svc
        from app.models.billing import BillingSubscription

        sub = MagicMock(spec=BillingSubscription)
        sub.id = uuid.uuid4()
        sub.status = "active"
        sub.stripe_subscription_id = None
        sub.cancelled_at = None

        db = _make_db_mock(first_result=sub)
        user = _make_user()

        with patch.dict(os.environ, {"STRIPE_API_KEY": "sk_test_fake", "STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            with patch("app.services.billing_service.stripe") as mock_stripe:
                resp = await svc.cancel_subscription(db, user, reason="switching")

        assert resp.status == "cancelled"
        mock_stripe.Subscription.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancel_subscription_not_found_raises(self):
        """No subscription in DB → ValueError('No subscription found')."""
        from app.services import billing_service as svc

        db = _make_db_mock(first_result=None)
        user = _make_user()

        with patch.dict(os.environ, {"STRIPE_API_KEY": "sk_test_fake", "STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            with pytest.raises(ValueError, match="No subscription found"):
                await svc.cancel_subscription(db, user, reason="test")


# ---------------------------------------------------------------------------
# 5. Route-level integration via TestClient
# ---------------------------------------------------------------------------

class TestBillingRoutes:
    """HTTP-level tests via async test client (conftest `client` fixture)."""

    @pytest.mark.asyncio
    async def test_checkout_route_no_auth_returns_401(self, client):
        """Unauthenticated POST /checkout-session → 401."""
        resp = await client.post(
            "/api/v1/billing/checkout-session",
            json={"tier": "professional", "return_url": "https://app.test"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_tiers_route_public(self, client):
        """GET /tiers public endpoint → 200 + list of tiers."""
        resp = await client.get("/api/v1/billing/tiers")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        tier_names = [t["name"] for t in data]
        assert "starter" in tier_names
        assert "professional" in tier_names
        assert "enterprise" in tier_names

    @pytest.mark.asyncio
    async def test_subscription_route_no_auth_returns_401(self, client):
        """Unauthenticated GET /subscription → 401."""
        resp = await client.get("/api/v1/billing/subscription")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_cancel_route_no_auth_returns_401(self, client):
        """Unauthenticated POST /cancel-subscription → 401."""
        resp = await client.post(
            "/api/v1/billing/cancel-subscription",
            json={"reason": "test"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_webhook_route_invalid_sig_returns_401(self, client):
        """POST /webhook with bad signature → 401."""
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_real"}):
            resp = await client.post(
                "/api/v1/billing/webhook",
                content=b'{"id":"evt_x"}',
                headers={"stripe-signature": "bad_sig", "content-type": "application/json"},
            )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_webhook_route_valid_sig_returns_200(self, client):
        """POST /webhook with valid signature → 200."""
        payload = json.dumps({"id": "evt_valid", "type": "unknown.event", "data": {"object": {}}}).encode()
        secret = "whsec_test_route"
        sig = _stripe_sig(payload, secret)

        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": secret}):
            with patch("app.services.billing_service.process_webhook", new_callable=AsyncMock) as mock_proc:
                mock_proc.return_value = True
                resp = await client.post(
                    "/api/v1/billing/webhook",
                    content=payload,
                    headers={"stripe-signature": sig, "content-type": "application/json"},
                )
        assert resp.status_code == 200
        data = resp.json()
        assert data["received"] is True


# ---------------------------------------------------------------------------
# 6. Pricing constants guard
# ---------------------------------------------------------------------------

class TestPricingConstants:
    """Guard TIER_PRICING constants to prevent accidental change."""

    def test_professional_price_correct(self):
        """Professional tier price must be 9900 cents ($99/mo)."""
        from app.services.billing_service import TIER_PRICING

        assert TIER_PRICING["professional"]["price"] == 9900

    def test_starter_price_correct(self):
        """Starter tier price must be 2900 cents ($29/mo)."""
        from app.services.billing_service import TIER_PRICING

        assert TIER_PRICING["starter"]["price"] == 2900

    def test_all_tiers_present(self):
        """All three tiers must be defined."""
        from app.services.billing_service import TIER_PRICING

        assert set(TIER_PRICING.keys()) == {"starter", "professional", "enterprise"}
