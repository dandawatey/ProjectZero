"""
Tests for claude-mem hook integration contract — PRJ0-72
TDD: written before implementation per factory contract.
"""
import pytest
from unittest.mock import patch, MagicMock
import urllib.error


# ---------------------------------------------------------------------------
# Tests for get_worker_url
# ---------------------------------------------------------------------------

def test_get_worker_url_default_port():
    from execution_console.app.integrations.claude.mem_hooks import get_worker_url
    assert get_worker_url() == "http://localhost:37777"


def test_get_worker_url_custom_port():
    from execution_console.app.integrations.claude.mem_hooks import get_worker_url
    assert get_worker_url(port=9999) == "http://localhost:9999"


def test_get_worker_url_includes_no_trailing_slash():
    from execution_console.app.integrations.claude.mem_hooks import get_worker_url
    url = get_worker_url()
    assert not url.endswith("/")


# ---------------------------------------------------------------------------
# Tests for is_worker_running
# ---------------------------------------------------------------------------

def test_is_worker_running_returns_true_when_health_ok():
    from execution_console.app.integrations.claude.mem_hooks import is_worker_running
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_response):
        assert is_worker_running() is True


def test_is_worker_running_returns_false_when_connection_refused():
    from execution_console.app.integrations.claude.mem_hooks import is_worker_running
    with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
        assert is_worker_running() is False


def test_is_worker_running_returns_false_on_url_error():
    from execution_console.app.integrations.claude.mem_hooks import is_worker_running
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("no route")):
        assert is_worker_running() is False


def test_is_worker_running_uses_custom_port():
    from execution_console.app.integrations.claude.mem_hooks import is_worker_running
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_open:
        is_worker_running(port=9999)
        called_url = mock_open.call_args[0][0]
        assert "9999" in called_url


# ---------------------------------------------------------------------------
# Tests for constants
# ---------------------------------------------------------------------------

def test_constants_defined():
    from execution_console.app.integrations.claude.mem_hooks import (
        WORKER_HEALTH,
        WORKER_OBSERVE,
        WORKER_SYNC,
        WORKER_COMPRESS,
        WORKER_FINALIZE,
    )
    assert WORKER_HEALTH == "/health"
    assert WORKER_OBSERVE == "/observe"
    assert WORKER_SYNC == "/sync"
    assert WORKER_COMPRESS == "/compress"
    assert WORKER_FINALIZE == "/finalize"
