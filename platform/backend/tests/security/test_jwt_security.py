"""JWT and auth security tests — PRJ0-69."""
import pytest
import jwt as pyjwt
import time
import os


@pytest.mark.asyncio
async def test_expired_jwt_returns_401(client):
    """Expired JWT must return 401, not 200."""
    secret = os.getenv("JWT_SECRET_KEY", "test-secret-key-32-chars-minimum!!")
    # Create expired token (iat/exp in past)
    expired_payload = {
        "sub": "test@example.com",
        "iat": int(time.time()) - 3600,
        "exp": int(time.time()) - 1800,  # expired 30min ago
    }
    expired_token = pyjwt.encode(expired_payload, secret, algorithm="HS256")
    client.headers["Authorization"] = f"Bearer {expired_token}"
    r = await client.get("/api/v1/agents")
    client.headers.pop("Authorization", None)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tampered_jwt_returns_401(client):
    """JWT with wrong signature must return 401."""
    fake_token = pyjwt.encode(
        {"sub": "attacker@evil.com", "exp": int(time.time()) + 3600},
        "wrong-secret-key",
        algorithm="HS256",
    )
    client.headers["Authorization"] = f"Bearer {fake_token}"
    r = await client.get("/api/v1/agents")
    client.headers.pop("Authorization", None)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_no_token_returns_401(client):
    r = await client.get("/api/v1/agents")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_malformed_bearer_returns_401(client):
    client.headers["Authorization"] = "Bearer not.a.real.token"
    r = await client.get("/api/v1/agents")
    client.headers.pop("Authorization", None)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_health_endpoint_public(client):
    """Health check must NOT require auth."""
    r = await client.get("/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_no_sensitive_data_in_health(client):
    """Health response must not leak secrets or config."""
    r = await client.get("/health")
    text = r.text.lower()
    assert "password" not in text
    assert "secret" not in text
    assert "token" not in text
    assert "postgresql" not in text
