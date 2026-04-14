"""Unit tests for MemBridge — PRJ0-75.

TDD stubs written before implementation per factory contract.
All HTTP calls mocked — no live services required.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call


class TestSyncPromotesHighScoreMemories(unittest.TestCase):
    """High-score memories (>= threshold) are promoted to Brain."""

    def test_sync_promotes_high_score_memories(self):
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        observations = [
            {"id": "obs-1", "content": "high value memory", "score": 0.85, "tags": ["arch"]},
            {"id": "obs-2", "content": "another high value", "score": 0.90, "tags": []},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "brain_sync.json"
            bridge = MemBridge(mem_port=37777, brain_url="http://localhost:8000", threshold=0.7)
            bridge._cursor_path = cursor_path

            mem_resp = MagicMock()
            mem_resp.status_code = 200
            mem_resp.json.return_value = {"memories": observations}

            brain_resp = MagicMock()
            brain_resp.status_code = 201
            brain_resp.json.return_value = {"id": "brain-uuid-1", "status": "stored"}

            with patch("httpx.get", return_value=mem_resp), \
                 patch("httpx.post", return_value=brain_resp):
                result = bridge.sync()

        assert result["synced"] == 2
        assert result["skipped"] == 0
        assert result["errors"] == 0
        assert result["dry_run"] is False


class TestSyncSkipsLowScoreMemories(unittest.TestCase):
    """Low-score memories (< threshold) are NOT promoted."""

    def test_sync_skips_low_score_memories(self):
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        observations = [
            {"id": "obs-low-1", "content": "low value memory", "score": 0.3, "tags": []},
            {"id": "obs-low-2", "content": "also low", "score": 0.65, "tags": []},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "brain_sync.json"
            bridge = MemBridge(mem_port=37777, brain_url="http://localhost:8000", threshold=0.7)
            bridge._cursor_path = cursor_path

            mem_resp = MagicMock()
            mem_resp.status_code = 200
            mem_resp.json.return_value = {"memories": observations}

            with patch("httpx.get", return_value=mem_resp), \
                 patch("httpx.post") as mock_post:
                result = bridge.sync()

        # Brain POST should never be called for low-score memories
        assert result["synced"] == 0
        assert result["skipped"] == 2
        mock_post.assert_not_called()


class TestSyncSkipsAlreadySynced(unittest.TestCase):
    """Memories already in cursor (dedup) are skipped."""

    def test_sync_skips_already_synced(self):
        import hashlib
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        content = "high value memory already synced"
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        observations = [
            {"id": "obs-dup", "content": content, "score": 0.95, "tags": []},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "brain_sync.json"
            # Pre-populate cursor with the hash
            cursor_path.write_text(json.dumps({
                "last_sync": "2026-04-14T00:00:00",
                "synced_hashes": [content_hash],
            }))

            bridge = MemBridge(mem_port=37777, brain_url="http://localhost:8000", threshold=0.7)
            bridge._cursor_path = cursor_path

            mem_resp = MagicMock()
            mem_resp.status_code = 200
            mem_resp.json.return_value = {"memories": observations}

            with patch("httpx.get", return_value=mem_resp), \
                 patch("httpx.post") as mock_post:
                result = bridge.sync()

        assert result["synced"] == 0
        assert result["skipped"] == 1
        mock_post.assert_not_called()


class TestSyncHandlesBrainUnavailable(unittest.TestCase):
    """Brain unreachable → errors counted, no exception raised to caller."""

    def test_sync_handles_brain_unavailable(self):
        import httpx as httpx_lib
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        observations = [
            {"id": "obs-3", "content": "good memory", "score": 0.80, "tags": []},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "brain_sync.json"
            bridge = MemBridge(mem_port=37777, brain_url="http://localhost:8000", threshold=0.7)
            bridge._cursor_path = cursor_path

            mem_resp = MagicMock()
            mem_resp.status_code = 200
            mem_resp.json.return_value = {"memories": observations}

            def side_effect(*args, **kwargs):
                # GET returns mem_resp, POST raises connection error
                if args and "memories" in str(args[0]):
                    return mem_resp
                raise httpx_lib.ConnectError("refused")

            with patch("httpx.get", return_value=mem_resp), \
                 patch("httpx.post", side_effect=httpx_lib.ConnectError("refused")):
                result = bridge.sync()  # must not raise

        assert result["errors"] == 1
        assert result["synced"] == 0


class TestContentHashDeterministic(unittest.TestCase):
    """SHA-256 hash of same content always produces same result."""

    def test_content_hash_deterministic(self):
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        bridge = MemBridge()
        content = "test memory content"
        h1 = bridge._content_hash(content)
        h2 = bridge._content_hash(content)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex = 64 chars

    def test_content_hash_different_for_different_content(self):
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        bridge = MemBridge()
        assert bridge._content_hash("content A") != bridge._content_hash("content B")


class TestDryRunDoesNotWrite(unittest.TestCase):
    """dry_run=True → no Brain POSTs, no cursor writes."""

    def test_dry_run_does_not_write(self):
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        observations = [
            {"id": "obs-dr", "content": "dry run memory", "score": 0.88, "tags": []},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "brain_sync.json"
            bridge = MemBridge(mem_port=37777, brain_url="http://localhost:8000", threshold=0.7)
            bridge._cursor_path = cursor_path

            mem_resp = MagicMock()
            mem_resp.status_code = 200
            mem_resp.json.return_value = {"memories": observations}

            with patch("httpx.get", return_value=mem_resp), \
                 patch("httpx.post") as mock_post:
                result = bridge.sync(dry_run=True)

        # No Brain POST
        mock_post.assert_not_called()
        # Cursor file not created
        assert not cursor_path.exists()
        # Result reports dry_run
        assert result["dry_run"] is True
        assert result["synced"] == 1  # would-be synced count


class TestCursorLoadSave(unittest.TestCase):
    """Cursor file persists synced hashes across calls."""

    def test_cursor_persists_synced_hashes(self):
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "brain_sync.json"
            bridge = MemBridge()
            bridge._cursor_path = cursor_path

            cursor = {"last_sync": "2026-04-14T00:00:00", "synced_hashes": ["abc123"]}
            bridge._save_cursor(cursor)
            loaded = bridge._load_cursor()

        assert loaded["synced_hashes"] == ["abc123"]

    def test_cursor_returns_empty_if_missing(self):
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "nonexistent.json"
            bridge = MemBridge()
            bridge._cursor_path = cursor_path
            loaded = bridge._load_cursor()

        assert loaded["synced_hashes"] == []


class TestMixedScoreSync(unittest.TestCase):
    """Mix of high/low score + already-synced → correct counts."""

    def test_mixed_score_sync_counts(self):
        import hashlib
        from execution_console.app.integrations.claude.mem_bridge import MemBridge

        already_synced_content = "already was synced"
        already_hash = hashlib.sha256(already_synced_content.encode()).hexdigest()

        observations = [
            {"id": "obs-high", "content": "fresh high value", "score": 0.91, "tags": []},
            {"id": "obs-low", "content": "low value junk", "score": 0.40, "tags": []},
            {"id": "obs-dup", "content": already_synced_content, "score": 0.95, "tags": []},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "brain_sync.json"
            cursor_path.write_text(json.dumps({
                "last_sync": "2026-04-14T00:00:00",
                "synced_hashes": [already_hash],
            }))

            bridge = MemBridge(mem_port=37777, brain_url="http://localhost:8000", threshold=0.7)
            bridge._cursor_path = cursor_path

            mem_resp = MagicMock()
            mem_resp.status_code = 200
            mem_resp.json.return_value = {"memories": observations}

            brain_resp = MagicMock()
            brain_resp.status_code = 201
            brain_resp.json.return_value = {"id": "brain-new", "status": "stored"}

            with patch("httpx.get", return_value=mem_resp), \
                 patch("httpx.post", return_value=brain_resp):
                result = bridge.sync()

        assert result["synced"] == 1   # only fresh high
        assert result["skipped"] == 2  # low + dup
        assert result["errors"] == 0


if __name__ == "__main__":
    unittest.main()
