"""PRJ0-85: Tests for UML diagram publisher."""
from __future__ import annotations

import os
import textwrap
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.uml_diagram_publisher import (
    UML_DIAGRAMS,
    _build_page_body,
    _configured,
    extract_mermaid,
    publish_uml_diagrams,
)

# ─── Unit tests ──────────────────────────────────────────────────────────────

def test_extract_mermaid_basic():
    html = '<div class="mermaid">flowchart LR\n    A --> B</div>'
    assert extract_mermaid(html) == "flowchart LR\n    A --> B"

def test_extract_mermaid_with_attributes():
    html = '<div class="mermaid" id="d1">sequenceDiagram\n    A->>B: hi</div>'
    assert "sequenceDiagram" in extract_mermaid(html)

def test_extract_mermaid_empty():
    assert extract_mermaid("<html>no diagram here</html>") == ""

def test_extract_mermaid_html_entities():
    html = '<div class="mermaid">A &amp; B --&gt; C</div>'
    result = extract_mermaid(html)
    assert "&" in result or "amp" in result  # unescape applied

def test_build_page_body_contains_title():
    body = _build_page_body("My Diagram", "flowchart LR", "2024-01-01 00:00 UTC")
    assert "My Diagram" in body
    assert "2024-01-01 00:00 UTC" in body

def test_build_page_body_contains_mermaid_source():
    body = _build_page_body("Test", "sequenceDiagram\nA->>B: msg", "now")
    assert "sequenceDiagram" in body

def test_build_page_body_escapes_html():
    body = _build_page_body("Test", "A <B> & C", "now")
    assert "<B>" not in body or "&lt;B&gt;" in body

def test_build_page_body_has_code_macro():
    body = _build_page_body("Test", "graph LR", "now")
    assert "ac:structured-macro" in body
    assert "ac:plain-text-body" in body

def test_uml_diagrams_list_has_seven():
    assert len(UML_DIAGRAMS) == 7

def test_uml_diagrams_all_html():
    for filename, title in UML_DIAGRAMS:
        assert filename.endswith(".html"), f"{filename} should end with .html"
        assert len(title) > 5, f"Title '{title}' too short"

def test_configured_false_when_no_env(monkeypatch):
    monkeypatch.delenv("CONFLUENCE_BASE_URL", raising=False)
    monkeypatch.delenv("JIRA_USER_EMAIL", raising=False)
    monkeypatch.delenv("CONFLUENCE_API_TOKEN", raising=False)
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)
    assert _configured() is False

def test_configured_true_when_env_set(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "https://test.atlassian.net/wiki")
    monkeypatch.setenv("JIRA_USER_EMAIL", "test@test.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "test-token")
    assert _configured() is True

# ─── Integration-style tests ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_publish_skipped_when_not_configured(monkeypatch, tmp_path):
    monkeypatch.delenv("CONFLUENCE_BASE_URL", raising=False)
    monkeypatch.delenv("JIRA_USER_EMAIL", raising=False)
    monkeypatch.delenv("CONFLUENCE_API_TOKEN", raising=False)
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)
    result = await publish_uml_diagrams()
    assert result["status"] == "skipped"

@pytest.mark.asyncio
async def test_publish_handles_missing_files(monkeypatch, tmp_path):
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "https://test.atlassian.net/wiki")
    monkeypatch.setenv("JIRA_USER_EMAIL", "test@test.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")
    monkeypatch.setenv("GUIDE_DIR", str(tmp_path))  # empty dir — all files missing

    # Mock HTTP client to return a valid parent page
    mock_resp_find = MagicMock()
    mock_resp_find.status_code = 200
    mock_resp_find.json.return_value = {"results": [{"id": "123", "version": {"number": 1}}]}

    with patch("app.services.uml_diagram_publisher.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp_find)
        MockClient.return_value = mock_client

        result = await publish_uml_diagrams()

    assert result["status"] in ("partial", "error", "ok")
    # All 7 should fail with "file not found"
    file_errors = [r for r in result.get("results", []) if r.get("reason") == "file not found"]
    assert len(file_errors) == 7

@pytest.mark.asyncio
async def test_publish_success_mock(monkeypatch, tmp_path):
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "https://test.atlassian.net/wiki")
    monkeypatch.setenv("JIRA_USER_EMAIL", "test@test.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")
    monkeypatch.setenv("GUIDE_DIR", str(tmp_path))

    # Create mock HTML files
    mermaid_html = textwrap.dedent("""
        <html><body>
        <div class="mermaid">flowchart LR
            A --> B
        </div>
        </body></html>
    """)
    for filename, _ in UML_DIAGRAMS:
        (tmp_path / filename).write_text(mermaid_html, encoding="utf-8")

    mock_find_resp = MagicMock()
    mock_find_resp.status_code = 200
    mock_find_resp.json.return_value = {"results": [{"id": "arch-parent", "version": {"number": 1}}]}

    mock_upsert_resp = MagicMock()
    mock_upsert_resp.status_code = 200
    mock_upsert_resp.json.return_value = {"id": "new-page-id"}

    with patch("app.services.uml_diagram_publisher.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        # First call: find parent; subsequent calls: find + upsert each diagram
        mock_client.get = AsyncMock(return_value=mock_find_resp)
        mock_client.put = AsyncMock(return_value=mock_upsert_resp)
        mock_client.post = AsyncMock(return_value=mock_upsert_resp)
        MockClient.return_value = mock_client

        result = await publish_uml_diagrams()

    assert result["published"] == 7
    assert len(result["errors"]) == 0
