"""Auth endpoint tests — PRJ0-64."""
import pytest


@pytest.mark.asyncio
async def test_register(client):
    r = await client.post("/api/v1/auth/register", json={
        "email": "new_reg@example.com", "password": "Pass123!", "full_name": "New User"
    })
    assert r.status_code in (200, 201)
    data = r.json()
    assert "access_token" in data or "id" in data or "email" in data


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login_ok@example.com", "password": "Pass123!", "full_name": "Login User"
    })
    r = await client.post("/api/v1/auth/login", json={
        "email": "login_ok@example.com", "password": "Pass123!"
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong_pw@example.com", "password": "Pass123!", "full_name": "Wrong"
    })
    r = await client.post("/api/v1/auth/login", json={
        "email": "wrong_pw@example.com", "password": "BadPass!"
    })
    assert r.status_code in (400, 401, 422)


@pytest.mark.asyncio
async def test_protected_route_no_token(client):
    r = await client.get("/api/v1/agents")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_invalid_token(client):
    client.headers["Authorization"] = "Bearer invalid.token.here"
    r = await client.get("/api/v1/agents")
    client.headers.pop("Authorization", None)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
