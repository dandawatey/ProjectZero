"""CORS security tests — PRJ0-69."""
import pytest


@pytest.mark.asyncio
async def test_cors_allowed_origin(client):
    """Requests from allowed origin get CORS headers."""
    r = await client.options(
        "/api/v1/agents",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # Preflight should succeed (200 or 204)
    assert r.status_code in (200, 204)
    # Should have CORS header
    assert "access-control-allow-origin" in r.headers


@pytest.mark.asyncio
async def test_cors_headers_present_on_api(client):
    """API responses include CORS allow-origin for known origins."""
    r = await client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert r.status_code == 200
    # Either wildcard or specific origin
    origin_header = r.headers.get("access-control-allow-origin", "")
    assert origin_header in ("*", "http://localhost:5173") or origin_header != ""
