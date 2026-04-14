"""Product endpoint tests — PRJ0-64.

Note: POST /api/v1/products only has /bootstrap and /prd-chat.
Direct product creation goes through /bootstrap.
GET /api/v1/products lists all products.
GET /api/v1/products/{id} fetches single product.
"""
import pytest


@pytest.mark.asyncio
async def test_list_products(auth_client):
    r = await auth_client.get("/api/v1/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_bootstrap_product(auth_client, tmp_path):
    """Bootstrap creates a product and returns its id."""
    repo = str(tmp_path / "test-product-prj0-64")
    r = await auth_client.post("/api/v1/products/bootstrap", json={
        "product_name": "Test Product PRJ0-64",
        "repo_path": repo,
        "jira_project_key": "TEST",
    })
    assert r.status_code in (200, 201)
    data = r.json()
    assert "id" in data
    assert data.get("name") == "Test Product PRJ0-64" or "repo_path" in data


@pytest.mark.asyncio
async def test_get_product(auth_client, tmp_path):
    """Bootstrap then fetch by ID."""
    repo = str(tmp_path / "get-test-prj0-64")
    r = await auth_client.post("/api/v1/products/bootstrap", json={
        "product_name": "Get Test Product PRJ0-64",
        "repo_path": repo,
    })
    assert r.status_code in (200, 201)
    product_id = r.json()["id"]

    r2 = await auth_client.get(f"/api/v1/products/{product_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == product_id
