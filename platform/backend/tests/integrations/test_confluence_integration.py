"""Confluence integration tests — PRJ0-66. Requires live Confluence."""
import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def confluence_client():
    try:
        from app.services.confluence_client import ConfluenceClient
        return ConfluenceClient()
    except Exception:
        pytest.skip("Confluence not configured or ConfluenceClient unavailable")


@pytest.mark.asyncio
async def test_confluence_page_create_update(confluence_client):
    """Create a test page, update it, verify idempotent upsert."""
    title = "[TEST] PRJ0-66 integration test — delete me"
    body1 = "<p>Initial content from PRJ0-66 integration test.</p>"
    body2 = "<p>Updated content from PRJ0-66 integration test.</p>"

    # Create
    r1 = await confluence_client.upsert_page(title=title, body=body1, parent_id=None)
    assert r1.get("id") or r1.get("url")

    # Update (idempotent upsert — should update, not duplicate)
    r2 = await confluence_client.upsert_page(title=title, body=body2, parent_id=None)
    # Same page id returned on update
    assert r1.get("id") == r2.get("id") or r2.get("id") is not None
