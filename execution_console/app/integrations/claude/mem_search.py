"""mem-search progressive disclosure implementation — PRJ0-74.

3-layer architecture:
  Layer 1 — search  (~50 tokens)   GET /search?q=&limit=
  Layer 2 — timeline (~200 tokens) GET /timeline?id=&window=
  Layer 3 — fetch   (full)         POST /fetch  {"ids": [...]}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import httpx

_WORKER_DOWN_MSG = (
    "claude-mem worker not running. "
    "Start with: npx claude-mem start"
)


@dataclass
class SearchResult:
    id: str
    snippet: str
    score: float
    timestamp: str
    token_estimate: int = 0
    content: Optional[str] = None


@dataclass
class SearchResponse:
    results: list[SearchResult]
    total: int
    layer: int  # 1, 2, or 3
    token_cost: int
    query: str = ""
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _worker_url(port: int) -> str:
    return f"http://localhost:{port}"


def _parse_results(raw: list[dict]) -> list[SearchResult]:
    out = []
    for item in raw:
        out.append(
            SearchResult(
                id=item.get("id", ""),
                snippet=item.get("snippet", ""),
                score=float(item.get("score", 0.0)),
                timestamp=item.get("timestamp", ""),
                content=item.get("content"),
            )
        )
    return out


# ---------------------------------------------------------------------------
# Layer 1 — search
# ---------------------------------------------------------------------------

def search(query: str, limit: int = 10, port: int = 37777) -> SearchResponse:
    """GET /search — cheap keyword/semantic search. Returns IDs + snippets."""
    url = f"{_worker_url(port)}/search"
    try:
        resp = httpx.get(url, params={"q": query, "limit": limit}, timeout=5.0)
        data = resp.json()
        results = _parse_results(data.get("results", []))
        return SearchResponse(
            results=results,
            total=data.get("total", len(results)),
            layer=1,
            token_cost=50,
            query=query,
        )
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return SearchResponse(
            results=[],
            total=0,
            layer=1,
            token_cost=0,
            query=query,
            error=_WORKER_DOWN_MSG,
        )


# ---------------------------------------------------------------------------
# Layer 2 — timeline
# ---------------------------------------------------------------------------

def timeline(obs_id: str, window: int = 5, port: int = 37777) -> SearchResponse:
    """GET /timeline — context window around a specific observation."""
    url = f"{_worker_url(port)}/timeline"
    try:
        resp = httpx.get(url, params={"id": obs_id, "window": window}, timeout=5.0)
        data = resp.json()
        results = _parse_results(data.get("results", []))
        return SearchResponse(
            results=results,
            total=data.get("total", len(results)),
            layer=2,
            token_cost=200,
            query=obs_id,
        )
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return SearchResponse(
            results=[],
            total=0,
            layer=2,
            token_cost=0,
            query=obs_id,
            error=_WORKER_DOWN_MSG,
        )


# ---------------------------------------------------------------------------
# Layer 3 — fetch
# ---------------------------------------------------------------------------

def fetch_ids(ids: list[str], port: int = 37777) -> SearchResponse:
    """POST /fetch — full content for explicitly selected observation IDs only."""
    url = f"{_worker_url(port)}/fetch"
    try:
        resp = httpx.post(url, json={"ids": ids}, timeout=10.0)
        data = resp.json()
        results = _parse_results(data.get("results", []))
        return SearchResponse(
            results=results,
            total=data.get("total", len(results)),
            layer=3,
            token_cost=len(results) * 500,  # rough estimate per observation
            query=",".join(ids),
        )
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return SearchResponse(
            results=[],
            total=0,
            layer=3,
            token_cost=0,
            query=",".join(ids),
            error=_WORKER_DOWN_MSG,
        )
