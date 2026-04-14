"""Execution Console API tests — PRJ0-70."""
import pytest
import sqlite3
from pathlib import Path
from unittest.mock import patch

import httpx


@pytest.fixture()
async def console_client(tmp_path):
    import execution_console.app.services.event_store as es
    db_path = str(tmp_path / "test_api.db")

    def _tmp_conn():
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(db_path)
        c.row_factory = sqlite3.Row
        return c

    with patch.object(es, "_conn", _tmp_conn):
        es.init_db()
        from execution_console.app.main import app
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as c:
            yield c


@pytest.mark.asyncio
async def test_health(console_client):
    r = await console_client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_ingest_event(console_client):
    r = await console_client.post("/api/v1/events", json={
        "event_type": "ticket_status",
        "ticket_id": "PRJ0-49",
        "status": "RUNNING",
        "pct": 45.0,
        "agent": "impl-agent",
    })
    assert r.status_code == 201
    assert r.json()["stored"] is True


@pytest.mark.asyncio
async def test_get_snapshot(console_client):
    r = await console_client.get("/api/v1/snapshot")
    assert r.status_code == 200
    data = r.json()
    assert "overall_pct" in data
    assert "features" in data
    assert "running_count" in data


@pytest.mark.asyncio
async def test_snapshot_reflects_failed_event(console_client):
    await console_client.post("/api/v1/events", json={
        "event_type": "ticket_status",
        "ticket_id": "PRJ0-52",
        "status": "FAILED",
        "pct": 0.0,
        "error": "test failure",
    })
    r = await console_client.get("/api/v1/snapshot")
    assert r.json()["failed_count"] >= 1


@pytest.mark.asyncio
async def test_clear_events(console_client):
    await console_client.post("/api/v1/events", json={
        "event_type": "step",
        "ticket_id": "PRJ0-53",
        "status": "RUNNING",
    })
    r = await console_client.delete("/api/v1/events")
    assert r.status_code == 200
    snap = await console_client.get("/api/v1/snapshot")
    assert snap.json()["running_count"] == 0


@pytest.mark.asyncio
async def test_failed_events_endpoint(console_client):
    await console_client.post("/api/v1/events", json={
        "event_type": "step",
        "ticket_id": "PRJ0-54",
        "status": "FAILED",
    })
    r = await console_client.get("/api/v1/events/failed")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    keys = [e["ticket_id"] for e in r.json()]
    assert "PRJ0-54" in keys


@pytest.mark.asyncio
async def test_ingest_event_minimal(console_client):
    """Minimal event (only event_type) accepted."""
    r = await console_client.post("/api/v1/events", json={"event_type": "step"})
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_snapshot_features_count(console_client):
    """Snapshot always contains the 6 feature groups."""
    r = await console_client.get("/api/v1/snapshot")
    data = r.json()
    assert len(data["features"]) == 6
