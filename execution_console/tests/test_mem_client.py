"""Unit tests for ClaudeMemClient — PRJ0-73.

TDD stubs written before implementation per factory contract.
All tests mock httpx to avoid requiring the worker to be running.
"""
from __future__ import annotations
import unittest
from unittest.mock import MagicMock, patch


class TestClaudeMemClientHealth(unittest.TestCase):
    """health() method tests."""

    def test_health_true_on_200(self):
        """Worker running → health returns True."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok"}
        with patch("httpx.get", return_value=mock_resp):
            client = ClaudeMemClient(port=37777)
            assert client.health() is True

    def test_health_false_on_connection_error(self):
        """Worker not running → health returns False, no exception raised."""
        import httpx
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        with patch("httpx.get", side_effect=httpx.ConnectError("refused")):
            client = ClaudeMemClient(port=37777)
            assert client.health() is False

    def test_health_false_on_non_200(self):
        """Worker returns non-200 → health returns False."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        with patch("httpx.get", return_value=mock_resp):
            client = ClaudeMemClient(port=37777)
            assert client.health() is False


class TestClaudeMemClientObserve(unittest.TestCase):
    """observe() method tests."""

    def test_observe_returns_id(self):
        """Successful POST /observe → returns observation ID string."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"id": "obs-abc123", "stored": True}
        with patch("httpx.post", return_value=mock_resp):
            client = ClaudeMemClient()
            result = client.observe("test observation", tags=["test", "prj0"])
            assert result == "obs-abc123"

    def test_observe_returns_none_on_error(self):
        """Connection error → observe returns None, no exception raised."""
        import httpx
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        with patch("httpx.post", side_effect=httpx.TimeoutException("timeout")):
            client = ClaudeMemClient()
            result = client.observe("will fail")
            assert result is None

    def test_observe_sends_tags(self):
        """observe() sends tags in request body."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"id": "obs-xyz", "stored": True}
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            client = ClaudeMemClient()
            client.observe("tagged obs", tags=["tag1", "tag2"])
            call_kwargs = mock_post.call_args
            body = call_kwargs[1].get("json") or call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1]["json"]
            assert "tag1" in body.get("tags", [])


class TestClaudeMemClientSearch(unittest.TestCase):
    """search() method tests."""

    def test_search_returns_observations(self):
        """Successful GET /search → list of MemObservation objects."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient, MemObservation
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [
                {"id": "obs-1", "content": "hello world", "score": 0.95,
                 "timestamp": "2026-04-14T10:00:00Z", "session_id": "s1", "tags": ["a"]},
                {"id": "obs-2", "content": "foo bar", "score": 0.80,
                 "timestamp": "2026-04-14T09:00:00Z", "session_id": None, "tags": []},
            ]
        }
        with patch("httpx.get", return_value=mock_resp):
            client = ClaudeMemClient()
            results = client.search("hello", limit=5)
            assert len(results) == 2
            assert isinstance(results[0], MemObservation)
            assert results[0].id == "obs-1"
            assert results[0].score == 0.95
            assert results[0].tags == ["a"]

    def test_search_returns_empty_on_timeout(self):
        """Timeout → search returns empty list, no exception raised."""
        import httpx
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        with patch("httpx.get", side_effect=httpx.TimeoutException("timeout")):
            client = ClaudeMemClient()
            results = client.search("anything")
            assert results == []

    def test_search_returns_empty_on_non_200(self):
        """Non-200 response → search returns empty list."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.json.return_value = {"error": "internal"}
        with patch("httpx.get", return_value=mock_resp):
            client = ClaudeMemClient()
            results = client.search("anything")
            assert results == []


class TestClaudeMemClientTimeline(unittest.TestCase):
    """get_timeline() method tests."""

    def test_get_timeline_returns_observations(self):
        """Successful GET /timeline → list of MemObservation objects."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient, MemObservation
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "observations": [
                {"id": "obs-a", "content": "before", "score": 1.0,
                 "timestamp": "2026-04-14T08:00:00Z", "session_id": None, "tags": []},
            ]
        }
        with patch("httpx.get", return_value=mock_resp):
            client = ClaudeMemClient()
            results = client.get_timeline("obs-center", window=3)
            assert len(results) == 1
            assert isinstance(results[0], MemObservation)

    def test_get_timeline_empty_on_error(self):
        """Connection error → get_timeline returns empty list."""
        import httpx
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        with patch("httpx.get", side_effect=httpx.ConnectError("refused")):
            client = ClaudeMemClient()
            assert client.get_timeline("obs-x") == []


class TestClaudeMemClientFetchByIds(unittest.TestCase):
    """fetch_by_ids() method tests."""

    def test_fetch_by_ids_returns_observations(self):
        """POST /fetch → list of MemObservation."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient, MemObservation
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "observations": [
                {"id": "obs-1", "content": "content1", "score": 1.0,
                 "timestamp": "2026-04-14T10:00:00Z", "session_id": "s1", "tags": ["x"]},
            ]
        }
        with patch("httpx.post", return_value=mock_resp):
            client = ClaudeMemClient()
            results = client.fetch_by_ids(["obs-1"])
            assert len(results) == 1
            assert results[0].id == "obs-1"

    def test_fetch_by_ids_empty_on_error(self):
        """Error → fetch_by_ids returns empty list."""
        import httpx
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
            client = ClaudeMemClient()
            assert client.fetch_by_ids(["obs-1"]) == []


class TestClaudeMemClientSyncCompress(unittest.TestCase):
    """sync() and compress() method tests."""

    def test_sync_returns_true_on_200(self):
        """POST /sync → True on success."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("httpx.post", return_value=mock_resp):
            client = ClaudeMemClient()
            assert client.sync() is True

    def test_sync_returns_false_on_error(self):
        """Connection error → sync returns False."""
        import httpx
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
            client = ClaudeMemClient()
            assert client.sync() is False

    def test_compress_returns_true_on_200(self):
        """POST /compress → True on success."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("httpx.post", return_value=mock_resp):
            client = ClaudeMemClient()
            assert client.compress() is True

    def test_compress_returns_false_on_error(self):
        """Connection error → compress returns False."""
        import httpx
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
            client = ClaudeMemClient()
            assert client.compress() is False


class TestClaudeMemClientListRecent(unittest.TestCase):
    """list_recent() method tests."""

    def test_list_recent_returns_observations(self):
        """GET /memories → list of MemObservation."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient, MemObservation
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "memories": [
                {"id": "obs-r1", "content": "recent1", "score": 1.0,
                 "timestamp": "2026-04-14T11:00:00Z", "session_id": None, "tags": []},
                {"id": "obs-r2", "content": "recent2", "score": 1.0,
                 "timestamp": "2026-04-14T10:30:00Z", "session_id": None, "tags": ["b"]},
            ]
        }
        with patch("httpx.get", return_value=mock_resp):
            client = ClaudeMemClient()
            results = client.list_recent(limit=10)
            assert len(results) == 2
            assert isinstance(results[0], MemObservation)

    def test_list_recent_empty_on_error(self):
        """Error → list_recent returns empty list."""
        import httpx
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        with patch("httpx.get", side_effect=httpx.ConnectError("refused")):
            client = ClaudeMemClient()
            assert client.list_recent() == []

    def test_list_recent_passes_since_param(self):
        """since param → forwarded to query string."""
        from execution_console.app.integrations.claude.mem_client import ClaudeMemClient
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"memories": []}
        with patch("httpx.get", return_value=mock_resp) as mock_get:
            client = ClaudeMemClient()
            client.list_recent(limit=5, since="2026-04-14T00:00:00Z")
            call_kwargs = mock_get.call_args
            params = call_kwargs[1].get("params", {})
            assert params.get("since") == "2026-04-14T00:00:00Z"


if __name__ == "__main__":
    unittest.main()
