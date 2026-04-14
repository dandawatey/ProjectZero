"""Secret leakage tests — PRJ0-69."""
import pytest


SENSITIVE_PATTERNS = [
    "password", "secret", "api_key", "apikey",
    "postgresql://", "database_url", "atatt",  # JIRA token prefix
    "traceback", "sqlalchemy", "asyncpg",
]


@pytest.mark.asyncio
async def test_health_no_secrets(client):
    r = await client.get("/health")
    body = r.text.lower()
    for pattern in SENSITIVE_PATTERNS:
        assert pattern not in body, f"Sensitive pattern '{pattern}' found in /health response"


@pytest.mark.asyncio
async def test_404_no_stack_trace(client):
    r = await client.get("/api/v1/nonexistent-endpoint-xyz")
    body = r.text.lower()
    assert "traceback" not in body
    assert "sqlalchemy" not in body


@pytest.mark.asyncio
async def test_401_response_no_secrets(client):
    client.headers["Authorization"] = "Bearer bad-token"
    r = await client.get("/api/v1/agents")
    client.headers.pop("Authorization", None)
    body = r.text.lower()
    for pattern in ["secret", "postgresql://", "traceback"]:
        assert pattern not in body


@pytest.mark.asyncio
async def test_error_response_no_db_connection_string(auth_client):
    """Error responses must not leak DB connection strings."""
    # Try to trigger a DB-related path
    r = await auth_client.get("/api/v1/products/99999999-0000-0000-0000-000000000000")
    body = r.text.lower()
    assert "postgresql://" not in body
    assert "asyncpg" not in body
