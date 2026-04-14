"""mem-search 3-layer progressive disclosure tests — PRJ0-74."""
from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest

from execution_console.app.integrations.claude.mem_search import (
    search,
    timeline,
    fetch_ids,
    SearchResult,
    SearchResponse,
)


# ---------------------------------------------------------------------------
# Layer 1 — search
# ---------------------------------------------------------------------------

def test_search_returns_response():
    """Layer 1 search returns SearchResponse with results list."""
    mock_payload = {
        "results": [
            {
                "id": "abc123",
                "snippet": "Fixed auth bug in login flow",
                "score": 0.95,
                "timestamp": "2026-04-14T10:00:00Z",
            }
        ],
        "total": 1,
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch(
        "execution_console.app.integrations.claude.mem_search.httpx.get",
        return_value=mock_resp,
    ):
        resp = search("auth bug")

    assert isinstance(resp, SearchResponse)
    assert resp.layer == 1
    assert resp.total == 1
    assert len(resp.results) == 1
    r = resp.results[0]
    assert isinstance(r, SearchResult)
    assert r.id == "abc123"
    assert r.score == 0.95
    assert resp.token_cost <= 100  # cheap layer


def test_search_handles_worker_down():
    """Layer 1 search returns empty response + error message when worker unavailable."""
    import httpx as _httpx

    with patch(
        "execution_console.app.integrations.claude.mem_search.httpx.get",
        side_effect=_httpx.ConnectError("connection refused"),
    ):
        resp = search("auth bug")

    assert isinstance(resp, SearchResponse)
    assert resp.results == []
    assert resp.total == 0
    assert resp.layer == 1
    assert resp.error is not None
    assert "worker" in resp.error.lower() or "running" in resp.error.lower()


# ---------------------------------------------------------------------------
# Layer 2 — timeline
# ---------------------------------------------------------------------------

def test_timeline_returns_context():
    """Layer 2 timeline returns window of observations around target."""
    mock_payload = {
        "results": [
            {
                "id": f"obs{i}",
                "snippet": f"observation {i}",
                "score": 1.0,
                "timestamp": "2026-04-14T10:00:00Z",
            }
            for i in range(11)  # 5 before + target + 5 after
        ],
        "total": 11,
        "center_id": "obs5",
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch(
        "execution_console.app.integrations.claude.mem_search.httpx.get",
        return_value=mock_resp,
    ):
        resp = timeline("obs5", window=5)

    assert isinstance(resp, SearchResponse)
    assert resp.layer == 2
    assert resp.total == 11
    assert resp.token_cost <= 300  # medium layer


# ---------------------------------------------------------------------------
# Layer 3 — fetch
# ---------------------------------------------------------------------------

def test_fetch_ids_returns_content():
    """Layer 3 fetch returns full content for selected IDs only."""
    mock_payload = {
        "results": [
            {
                "id": "abc123",
                "snippet": "Full content of observation abc123 with all details",
                "score": 1.0,
                "timestamp": "2026-04-14T10:00:00Z",
                "content": "Complete observation content here",
            },
            {
                "id": "def456",
                "snippet": "Full content of observation def456",
                "score": 1.0,
                "timestamp": "2026-04-14T11:00:00Z",
                "content": "Another complete observation",
            },
        ],
        "total": 2,
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch(
        "execution_console.app.integrations.claude.mem_search.httpx.post",
        return_value=mock_resp,
    ):
        resp = fetch_ids(["abc123", "def456"])

    assert isinstance(resp, SearchResponse)
    assert resp.layer == 3
    assert resp.total == 2
    assert len(resp.results) == 2
    ids = [r.id for r in resp.results]
    assert "abc123" in ids
    assert "def456" in ids


def test_fetch_ids_handles_worker_down():
    """Layer 3 fetch gracefully handles worker unavailability."""
    import httpx as _httpx

    with patch(
        "execution_console.app.integrations.claude.mem_search.httpx.post",
        side_effect=_httpx.ConnectError("connection refused"),
    ):
        resp = fetch_ids(["abc123"])

    assert isinstance(resp, SearchResponse)
    assert resp.results == []
    assert resp.layer == 3
    assert resp.error is not None
