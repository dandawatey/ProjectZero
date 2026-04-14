"""Commands endpoint tests — PRJ0-64."""
import pytest


@pytest.mark.asyncio
async def test_check_command(auth_client):
    r = await auth_client.post("/api/v1/commands/check", json={
        "repo_path": "/tmp",
        "product_id": "test",
    })
    assert r.status_code == 200
    data = r.json()
    assert "passed" in data
    assert "gates" in data
    assert isinstance(data["gates"], list)


@pytest.mark.asyncio
async def test_sprint_command(auth_client):
    r = await auth_client.get("/api/v1/commands/sprint")
    # May fail if JIRA not configured — just check it doesn't 500
    assert r.status_code in (200, 400, 422, 503)


@pytest.mark.asyncio
async def test_sprint_plan_command(auth_client):
    r = await auth_client.get("/api/v1/commands/sprint-plan")
    assert r.status_code in (200, 400, 422, 503)


@pytest.mark.asyncio
async def test_status_command(auth_client):
    r = await auth_client.get("/api/v1/commands/status/nonexistent-product")
    # Returns 200 with "No workflow runs found" message, or 404
    assert r.status_code in (200, 404)


@pytest.mark.asyncio
async def test_agent_map_command(auth_client):
    r = await auth_client.get("/api/v1/commands/agent-map")
    assert r.status_code == 200
    data = r.json()
    assert "stages" in data
    assert "stage_order" in data
