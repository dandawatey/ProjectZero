"""
Brain ↔ claude-mem sync bridge — PRJ0-75.

Promotes high-value claude-mem memories (score >= threshold) to Postgres Brain.
Runs at session end (Stop hook) or on-demand.

NORMAL MODE:
  Get memories from claude-mem worker scored >= CLAUDE_MEM_BRAIN_THRESHOLD (0.7)
  For each: hash content, check not already in Brain (dedup)
  POST to Brain API /api/v1/brain/memories
  Record sync cursor in ~/.claude-mem/brain_sync.json

CAVEMAN MODE:
  Good memories found. Not already saved? Send to Brain. Mark as synced.
  Next session: skip already-sent memories. No duplicates.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_CURSOR_PATH = Path.home() / ".claude-mem" / "brain_sync.json"

# Env-var overrides (mirrors Config pattern)
_DEFAULT_MEM_PORT = int(os.getenv("CLAUDE_MEM_PORT", "37777"))
_DEFAULT_BRAIN_URL = os.getenv("PROJECTZERO_BASE_URL", "http://localhost:8000")
_DEFAULT_BRAIN_TOKEN = os.getenv("PROJECTZERO_TOKEN", "")
_DEFAULT_THRESHOLD = float(os.getenv("CLAUDE_MEM_BRAIN_THRESHOLD", "0.7"))


class MemBridge:
    """
    Sync high-value claude-mem memories to Postgres Brain.

    Usage:
        bridge = MemBridge()
        result = bridge.sync()           # live sync
        result = bridge.sync(dry_run=True)  # preview without writing
    """

    def __init__(
        self,
        mem_port: int = _DEFAULT_MEM_PORT,
        brain_url: str = _DEFAULT_BRAIN_URL,
        brain_token: str = _DEFAULT_BRAIN_TOKEN,
        threshold: float = _DEFAULT_THRESHOLD,
    ) -> None:
        self._mem_base = f"http://localhost:{mem_port}"
        self._brain_base = brain_url.rstrip("/")
        self._brain_token = brain_token
        self._threshold = threshold
        # Allow tests to override cursor path
        self._cursor_path: Path = _DEFAULT_CURSOR_PATH

    # ── Public ────────────────────────────────────────────────────────────────

    def sync(self, dry_run: bool = False) -> dict:
        """
        Sync high-value memories to Brain.

        Returns:
            {"synced": N, "skipped": N, "errors": N, "dry_run": bool}
        """
        synced = 0
        skipped = 0
        errors = 0

        memories = self._get_memories_above_threshold()
        cursor = self._load_cursor()

        for mem in memories:
            content = mem.get("content", "")
            if not content:
                skipped += 1
                continue

            h = self._content_hash(content)
            if self._is_already_synced(h, cursor):
                skipped += 1
                continue

            if dry_run:
                synced += 1
                continue

            ok = self._promote_to_brain(mem)
            if ok:
                self._mark_synced(mem.get("id", ""), h, cursor)
                synced += 1
            else:
                errors += 1

        if not dry_run:
            self._save_cursor(cursor)

        return {"synced": synced, "skipped": skipped, "errors": errors, "dry_run": dry_run}

    # ── Private ───────────────────────────────────────────────────────────────

    def _get_memories_above_threshold(self) -> list[dict]:
        """Fetch all recent memories from claude-mem worker, filter by score."""
        try:
            resp = httpx.get(
                f"{self._mem_base}/memories",
                params={"limit": 500},
                timeout=10.0,
            )
            if resp.status_code != 200:
                logger.warning("claude-mem /memories returned %s", resp.status_code)
                return []
            data = resp.json()
            all_mems: list[dict] = data.get("memories", [])
            return [m for m in all_mems if float(m.get("score", 0.0)) >= self._threshold]
        except Exception as exc:
            logger.warning("Failed to fetch claude-mem memories: %s", exc)
            return []

    def _content_hash(self, content: str) -> str:
        """SHA-256 of content string. Deterministic dedup key."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _is_already_synced(self, content_hash: str, cursor: Optional[dict] = None) -> bool:
        """Return True if content_hash is in the sync cursor."""
        if cursor is None:
            cursor = self._load_cursor()
        return content_hash in cursor.get("synced_hashes", [])

    def _promote_to_brain(self, memory: dict) -> bool:
        """POST memory to Brain API. Returns True on success, False on any error."""
        try:
            headers: dict = {"Content-Type": "application/json"}
            if self._brain_token:
                headers["Authorization"] = f"Bearer {self._brain_token}"

            payload = {
                "scope": "session",
                "category": memory.get("category", "learning"),
                "title": (memory.get("content", "")[:80] or "claude-mem observation"),
                "content": memory["content"],
                "tags": memory.get("tags", []),
                "source_agent": "claude-mem-bridge",
                "confidence": float(memory.get("score", 0.8)),
                "promotion_status": "local",
            }

            resp = httpx.post(
                f"{self._brain_base}/api/v1/brain/memory",
                json=payload,
                headers=headers,
                timeout=10.0,
            )
            if resp.status_code in (200, 201):
                return True
            logger.warning("Brain POST returned %s: %s", resp.status_code, resp.text[:200])
            return False
        except Exception as exc:
            logger.warning("Brain POST failed: %s", exc)
            return False

    def _mark_synced(self, memory_id: str, content_hash: str, cursor: dict) -> None:
        """Append content_hash to cursor in-place (mutates cursor dict)."""
        hashes: list = cursor.setdefault("synced_hashes", [])
        if content_hash not in hashes:
            hashes.append(content_hash)
        cursor["last_sync"] = datetime.now(timezone.utc).isoformat()

    def _load_cursor(self) -> dict:
        """Load sync cursor from disk. Returns empty cursor if missing/corrupt."""
        try:
            if self._cursor_path.exists():
                data = json.loads(self._cursor_path.read_text())
                if "synced_hashes" not in data:
                    data["synced_hashes"] = []
                return data
        except Exception as exc:
            logger.warning("Failed to load cursor %s: %s", self._cursor_path, exc)
        return {"last_sync": None, "synced_hashes": []}

    def _save_cursor(self, cursor: dict) -> None:
        """Persist sync cursor to disk. Creates parent dirs as needed."""
        try:
            self._cursor_path.parent.mkdir(parents=True, exist_ok=True)
            self._cursor_path.write_text(json.dumps(cursor, indent=2))
        except Exception as exc:
            logger.warning("Failed to save cursor %s: %s", self._cursor_path, exc)
