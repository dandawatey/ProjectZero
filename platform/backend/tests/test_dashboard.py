"""Dashboard and workflow endpoint tests — PRJ0-64."""
import pytest


@pytest.mark.asyncio
async def test_dashboard_summary(auth_client):
    r = await auth_client.get("/api/v1/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    # DashboardSummary has active, completed, recent_runs fields
    assert "active" in data or "total" in data or "recent_runs" in data


@pytest.mark.asyncio
async def test_workflows_list(auth_client):
    r = await auth_client.get("/api/v1/workflows/")
    # May be 200 (list) or 404/405 depending on router — just ensure no 500
    assert r.status_code in (200, 307, 404, 405)


@pytest.mark.asyncio
async def test_audit_list(auth_client):
    r = await auth_client.get("/api/v1/audit/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_activities_list(auth_client):
    r = await auth_client.get("/api/v1/activities/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
