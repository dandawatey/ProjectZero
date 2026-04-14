"""claude-mem → Brain sync bridge — PRJ0-71.

Reads high-value observations and session summaries from the claude-mem
SQLite DB (~/.claude-mem/claude-mem.db) and promotes them to the
ProjectZero Brain (Postgres-backed, /api/v1/brain/memories).

Promotion criteria:
  observations    : relevance_count >= 2
  session_summaries: always (one per session, compact)

Deduplication: content_hash tracked in Brain via memory.key field.
Safe to run multiple times — already-synced entries are skipped.

Usage:
  python -m app.services.claude_mem_sync          # sync now
  python -m app.services.claude_mem_sync --dry-run # print what would sync
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CLAUDE_MEM_DB = Path(os.getenv("CLAUDE_MEM_DATA_DIR", str(Path.home() / ".claude-mem"))) / "claude-mem.db"
BRAIN_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
BRAIN_MEMORIES_URL = f"{BRAIN_BASE}/api/v1/brain/memories"
RELEVANCE_THRESHOLD = int(os.getenv("CLAUDE_MEM_SYNC_RELEVANCE_MIN", "2"))
FACTORY_PRODUCT_ID = os.getenv("CLAUDE_MEM_SYNC_PRODUCT_ID", "factory")


# ---------------------------------------------------------------------------
# Read from claude-mem SQLite
# ---------------------------------------------------------------------------

def _open_db() -> sqlite3.Connection | None:
    if not CLAUDE_MEM_DB.exists():
        logger.warning("claude-mem DB not found at %s", CLAUDE_MEM_DB)
        return None
    try:
        return sqlite3.connect(str(CLAUDE_MEM_DB), check_same_thread=False)
    except Exception as exc:
        logger.warning("Cannot open claude-mem DB: %s", exc)
        return None


def _fetch_observations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return high-relevance observations as dicts."""
    try:
        rows = conn.execute(
            """
            SELECT id, title, subtitle, text, facts, narrative, concepts,
                   files_modified, relevance_count, content_hash, project,
                   created_at, generated_by_model, type
            FROM observations
            WHERE relevance_count >= ?
            ORDER BY relevance_count DESC, created_at DESC
            """,
            (RELEVANCE_THRESHOLD,),
        ).fetchall()
        cols = [
            "id", "title", "subtitle", "text", "facts", "narrative", "concepts",
            "files_modified", "relevance_count", "content_hash", "project",
            "created_at", "generated_by_model", "type",
        ]
        return [dict(zip(cols, row)) for row in rows]
    except Exception as exc:
        logger.warning("observations query failed: %s", exc)
        return []


def _fetch_session_summaries(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return recent session summaries."""
    try:
        rows = conn.execute(
            """
            SELECT id, memory_session_id, project, request, investigated,
                   learned, completed, next_steps, notes, created_at
            FROM session_summaries
            ORDER BY created_at DESC
            LIMIT 50
            """,
        ).fetchall()
        cols = [
            "id", "memory_session_id", "project", "request", "investigated",
            "learned", "completed", "next_steps", "notes", "created_at",
        ]
        return [dict(zip(cols, row)) for row in rows]
    except Exception as exc:
        logger.warning("session_summaries query failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Brain API helpers
# ---------------------------------------------------------------------------

def _existing_keys(client: httpx.Client, product_id: str) -> set[str]:
    """Fetch keys already in Brain for this product to deduplicate."""
    try:
        r = client.get(
            BRAIN_MEMORIES_URL,
            params={"scope": "product", "product_id": product_id, "limit": 500},
            timeout=15,
        )
        if r.status_code == 200:
            return {m.get("key", "") for m in r.json()}
    except Exception as exc:
        logger.warning("Brain fetch failed: %s", exc)
    return set()


def _post_memory(client: httpx.Client, payload: dict) -> bool:
    try:
        r = client.post(BRAIN_MEMORIES_URL, json=payload, timeout=15)
        if r.status_code in (200, 201):
            return True
        logger.warning("Brain POST failed %s: %s", r.status_code, r.text[:200])
        return False
    except Exception as exc:
        logger.warning("Brain POST exception: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------

def _obs_to_payload(obs: dict[str, Any]) -> dict:
    content_parts = []
    if obs.get("title"):
        content_parts.append(f"# {obs['title']}")
    if obs.get("subtitle"):
        content_parts.append(obs["subtitle"])
    if obs.get("narrative"):
        content_parts.append(obs["narrative"])
    if obs.get("facts"):
        try:
            facts = json.loads(obs["facts"]) if isinstance(obs["facts"], str) else obs["facts"]
            if isinstance(facts, list):
                content_parts.extend(f"- {f}" for f in facts[:10])
        except Exception:
            content_parts.append(str(obs["facts"])[:500])
    if obs.get("files_modified"):
        content_parts.append(f"Files: {obs['files_modified']}")

    content = "\n".join(content_parts)[:2000]
    key = f"claude-mem:obs:{obs.get('content_hash') or hashlib.sha1(content.encode()).hexdigest()[:12]}"

    return {
        "key": key,
        "content": content,
        "category": "observation",
        "scope": "factory",
        "product_id": FACTORY_PRODUCT_ID,
        "metadata": {
            "source": "claude-mem",
            "type": obs.get("type", "observation"),
            "project": obs.get("project", ""),
            "relevance_count": obs.get("relevance_count", 0),
            "concepts": obs.get("concepts", ""),
            "created_at": obs.get("created_at", ""),
        },
    }


def _summary_to_payload(summ: dict[str, Any]) -> dict:
    parts = []
    if summ.get("request"):
        parts.append(f"Request: {summ['request']}")
    if summ.get("investigated"):
        parts.append(f"Investigated: {summ['investigated']}")
    if summ.get("learned"):
        parts.append(f"Learned: {summ['learned']}")
    if summ.get("completed"):
        parts.append(f"Completed: {summ['completed']}")
    if summ.get("next_steps"):
        parts.append(f"Next steps: {summ['next_steps']}")
    if summ.get("notes"):
        parts.append(f"Notes: {summ['notes']}")

    content = "\n".join(parts)[:2000]
    raw_key = f"claude-mem:session:{summ.get('memory_session_id', summ.get('id', ''))}"
    key = raw_key[:128]

    return {
        "key": key,
        "content": content,
        "category": "session_summary",
        "scope": "factory",
        "product_id": FACTORY_PRODUCT_ID,
        "metadata": {
            "source": "claude-mem",
            "type": "session_summary",
            "project": summ.get("project", ""),
            "session_id": str(summ.get("memory_session_id", "")),
            "created_at": summ.get("created_at", ""),
        },
    }


def sync(dry_run: bool = False) -> dict[str, int]:
    """Main sync entry point. Returns counts dict."""
    conn = _open_db()
    if conn is None:
        return {"skipped": 1, "reason": "db_not_found"}

    observations = _fetch_observations(conn)
    summaries = _fetch_session_summaries(conn)
    conn.close()

    logger.info(
        "claude-mem sync: %d observations (relevance>=%d), %d summaries",
        len(observations), RELEVANCE_THRESHOLD, len(summaries),
    )

    if not observations and not summaries:
        return {"synced": 0, "skipped": 0}

    counts = {"synced": 0, "skipped": 0, "failed": 0}

    if dry_run:
        for obs in observations:
            p = _obs_to_payload(obs)
            print(f"[DRY] observation: {p['key']} — {p['content'][:80]}")
        for s in summaries:
            p = _summary_to_payload(s)
            print(f"[DRY] summary: {p['key']} — {p['content'][:80]}")
        return {"dry_run": len(observations) + len(summaries)}

    with httpx.Client() as client:
        existing = _existing_keys(client, FACTORY_PRODUCT_ID)

        for obs in observations:
            payload = _obs_to_payload(obs)
            if payload["key"] in existing:
                counts["skipped"] += 1
                continue
            if _post_memory(client, payload):
                counts["synced"] += 1
            else:
                counts["failed"] += 1

        for summ in summaries:
            payload = _summary_to_payload(summ)
            if payload["key"] in existing:
                counts["skipped"] += 1
                continue
            if _post_memory(client, payload):
                counts["synced"] += 1
            else:
                counts["failed"] += 1

    logger.info("claude-mem sync complete: %s", counts)
    return counts


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Sync claude-mem → Brain")
    parser.add_argument("--dry-run", action="store_true", help="Print what would sync, don't write")
    args = parser.parse_args()
    result = sync(dry_run=args.dry_run)
    print(f"Sync result: {result}")
