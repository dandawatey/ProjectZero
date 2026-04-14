"""claude-mem worker HTTP client — PRJ0-73.

Talks to the claude-mem Node.js worker (default port 37777).
All methods return empty/False if worker unreachable — never raise.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MemObservation:
    """Single observation stored in claude-mem worker."""
    id: str
    content: str
    score: float
    timestamp: str
    session_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)


def _parse_observations(items: list[dict]) -> list[MemObservation]:
    """Convert raw dicts → MemObservation list, skip malformed entries."""
    results: list[MemObservation] = []
    for item in items:
        try:
            results.append(MemObservation(
                id=item["id"],
                content=item.get("content", ""),
                score=float(item.get("score", 1.0)),
                timestamp=item.get("timestamp", ""),
                session_id=item.get("session_id"),
                tags=item.get("tags", []),
            ))
        except (KeyError, TypeError, ValueError) as exc:
            logger.debug("Skip malformed observation: %s — %s", item, exc)
    return results


class ClaudeMemClient:
    """HTTP client for the claude-mem worker API.

    Worker runs on localhost at `port` (default 37777).
    All methods are graceful: connection errors → return empty value, log debug.
    """

    def __init__(self, port: int = 37777, timeout: float = 3.0) -> None:
        self._base = f"http://localhost:{port}"
        self._timeout = timeout

    # ── Health ──────────────────────────────────────────────────────────────

    def health(self) -> bool:
        """GET /health → True if worker running and healthy."""
        try:
            r = httpx.get(f"{self._base}/health", timeout=self._timeout)
            return r.status_code == 200
        except Exception as exc:
            logger.debug("claude-mem health check failed: %s", exc)
            return False

    # ── Write ───────────────────────────────────────────────────────────────

    def observe(self, content: str, tags: list[str] | None = None) -> Optional[str]:
        """POST /observe → observation ID string, or None on error."""
        try:
            payload: dict = {"content": content, "tags": tags or []}
            r = httpx.post(f"{self._base}/observe", json=payload, timeout=self._timeout)
            if r.status_code in (200, 201):
                return r.json().get("id")
            logger.debug("claude-mem observe non-2xx: %s", r.status_code)
            return None
        except Exception as exc:
            logger.debug("claude-mem observe error: %s", exc)
            return None

    # ── Read ────────────────────────────────────────────────────────────────

    def search(self, query: str, limit: int = 10) -> list[MemObservation]:
        """GET /search?q=...&limit=... → list of MemObservation."""
        try:
            r = httpx.get(
                f"{self._base}/search",
                params={"q": query, "limit": limit},
                timeout=self._timeout,
            )
            if r.status_code == 200:
                return _parse_observations(r.json().get("results", []))
            logger.debug("claude-mem search non-200: %s", r.status_code)
            return []
        except Exception as exc:
            logger.debug("claude-mem search error: %s", exc)
            return []

    def get_timeline(self, obs_id: str, window: int = 5) -> list[MemObservation]:
        """GET /timeline?id=...&window=... → surrounding observations."""
        try:
            r = httpx.get(
                f"{self._base}/timeline",
                params={"id": obs_id, "window": window},
                timeout=self._timeout,
            )
            if r.status_code == 200:
                return _parse_observations(r.json().get("observations", []))
            logger.debug("claude-mem timeline non-200: %s", r.status_code)
            return []
        except Exception as exc:
            logger.debug("claude-mem timeline error: %s", exc)
            return []

    def fetch_by_ids(self, ids: list[str]) -> list[MemObservation]:
        """POST /fetch with ids list → full observations."""
        try:
            r = httpx.post(
                f"{self._base}/fetch",
                json={"ids": ids},
                timeout=self._timeout,
            )
            if r.status_code == 200:
                return _parse_observations(r.json().get("observations", []))
            logger.debug("claude-mem fetch non-200: %s", r.status_code)
            return []
        except Exception as exc:
            logger.debug("claude-mem fetch_by_ids error: %s", exc)
            return []

    def list_recent(
        self, limit: int = 20, since: Optional[str] = None
    ) -> list[MemObservation]:
        """GET /memories?limit=...&since=... → recent observations."""
        try:
            params: dict = {"limit": limit}
            if since:
                params["since"] = since
            r = httpx.get(f"{self._base}/memories", params=params, timeout=self._timeout)
            if r.status_code == 200:
                return _parse_observations(r.json().get("memories", []))
            logger.debug("claude-mem list_recent non-200: %s", r.status_code)
            return []
        except Exception as exc:
            logger.debug("claude-mem list_recent error: %s", exc)
            return []

    # ── Admin ───────────────────────────────────────────────────────────────

    def sync(self) -> bool:
        """POST /sync → trigger Brain sync. Returns True on success."""
        try:
            r = httpx.post(f"{self._base}/sync", timeout=self._timeout)
            return r.status_code == 200
        except Exception as exc:
            logger.debug("claude-mem sync error: %s", exc)
            return False

    def compress(self) -> bool:
        """POST /compress → trigger memory compression. Returns True on success."""
        try:
            r = httpx.post(f"{self._base}/compress", timeout=self._timeout)
            return r.status_code == 200
        except Exception as exc:
            logger.debug("claude-mem compress error: %s", exc)
            return False
