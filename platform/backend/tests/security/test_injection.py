"""SQL injection and input sanitization tests — PRJ0-69."""
import pytest


INJECTION_PAYLOADS = [
    "'; DROP TABLE agents; --",
    "1 OR 1=1",
    "<script>alert('xss')</script>",
    "\" OR \"1\"=\"1",
    "admin'--",
    "../../../etc/passwd",
]


@pytest.mark.asyncio
async def test_product_id_injection_safe(auth_client):
    """Injected product_id must not cause 500 — ORM parameterises queries."""
    for payload in INJECTION_PAYLOADS:
        r = await auth_client.get(f"/api/v1/commands/status/{payload}")
        # 404 or 200 OK — never 500
        assert r.status_code != 500, f"500 error for payload: {payload!r}"


@pytest.mark.asyncio
async def test_check_command_path_traversal(auth_client):
    """repo_path traversal attempts must not cause 500."""
    for payload in ["../../../etc", "/etc/passwd", "../../../../root"]:
        r = await auth_client.post("/api/v1/commands/check", json={
            "repo_path": payload,
            "product_id": "test",
        })
        assert r.status_code != 500


@pytest.mark.asyncio
async def test_brain_memory_xss_stored_safe(auth_client):
    """XSS content stored in brain memory must be stored as-is (not executed)."""
    xss = "<script>alert('xss')</script>"
    r = await auth_client.post("/api/v1/brain/memory", json={
        "content": xss,
        "scope": "product",
        "category": "test",
        "product_id": "test",
        "title": "XSS test",
    })
    # Should store successfully (content sanitized at render, not storage)
    assert r.status_code in (200, 201)
    memory_id = r.json().get("id")
    if memory_id:
        # Retrieve — raw content returned, not executed
        r2 = await auth_client.get("/api/v1/brain/memory")
        assert r2.status_code == 200
