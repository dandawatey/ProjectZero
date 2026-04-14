"""Brain endpoint tests — PRJ0-64."""
import pytest


@pytest.mark.asyncio
async def test_store_memory(auth_client):
    r = await auth_client.post("/api/v1/brain/memory", json={
        "content": "Test memory content for PRJ0-64",
        "scope": "product",
        "category": "test",
        "product_id": "test-product-id",
        "title": "Test Memory PRJ0-64",
    })
    assert r.status_code in (200, 201)
    data = r.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_list_memories(auth_client):
    # brain uses /memory (singular) for GET
    r = await auth_client.get("/api/v1/brain/memory")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_pending_promotions(auth_client):
    r = await auth_client.get("/api/v1/brain/memories/pending-promotion")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_factory_scope_filter(auth_client):
    r = await auth_client.get("/api/v1/brain/memory?scope=factory")
    assert r.status_code == 200
    data = r.json()
    # All returned memories should be approved promotions
    for m in data:
        assert m.get("promotion_status") == "approved" or m.get("promoted") is True
