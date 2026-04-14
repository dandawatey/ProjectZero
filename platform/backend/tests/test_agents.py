"""Agent endpoint tests — PRJ0-64."""
import pytest


@pytest.mark.asyncio
async def test_list_agents(auth_client):
    r = await auth_client.get("/api/v1/agents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_list_skills(auth_client):
    r = await auth_client.get("/api/v1/agents/skills")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # skill catalog uses "id" key (not "skill_id")
    skill_ids = [s.get("id") or s.get("skill_id") for s in data]
    for expected in ["spec", "arch", "implement", "review", "deploy"]:
        assert expected in skill_ids


@pytest.mark.asyncio
async def test_list_executions(auth_client):
    r = await auth_client.get("/api/v1/agents/executions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_create_agent(auth_client):
    r = await auth_client.post("/api/v1/agents", json={
        "agent_id": "test-agent-unique-64",
        "name": "Test Agent PRJ0-64",
        "skills": ["test"],
        "model": "claude-sonnet-4-6",
        "status": "active",
    })
    assert r.status_code in (200, 201)
    data = r.json()
    assert data.get("agent_id") == "test-agent-unique-64"
