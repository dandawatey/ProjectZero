"""AgentDispatcher — PRJ0-51.

Replaces raw _call_claude() calls in Temporal activities.
Fully synchronous — activities run in thread pool executor.

Flow per dispatch:
  1. Resolve skill definition from skill_registry
  2. Read Brain memories for context
  3. Build user prompt
  4. Call Claude (via _call_claude from activities)
  5. Quality gate — retry once on failure
  6. Write result summary to Brain (best-effort)
  7. Update agent last_used_at in DB (best-effort)
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class AgentDispatcher:
    """Sync dispatcher — safe to call from thread pool executor."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        skill_id: str,
        product_id: str,
        feature_id: str,
        context_str: str,
        repo_path: str = "",
    ) -> str:
        """Dispatch a skill call end-to-end. Returns Claude output string."""
        from app.services.skill_registry import get_skill
        from app.temporal_integration.activities import _call_claude

        # 1. Resolve skill
        skill = get_skill(skill_id)

        # 2. Read Brain
        brain_ctx = self._read_brain(product_id, skill_id)

        # 3. Build prompt
        user_prompt = (
            f"Feature: {feature_id}\n"
            f"Product: {product_id}\n"
            f"Brain context:\n{brain_ctx}\n\n"
            f"Context:\n{context_str}"
        )

        # 4. Call Claude
        output = _call_claude(skill.system_prompt, user_prompt)

        # 5. Quality gate — retry once on failure
        try:
            skill.quality_gate(output)
        except ValueError as exc:
            logger.warning(
                "Quality gate failed for skill=%s, feature=%s: %s — retrying",
                skill_id,
                feature_id,
                exc,
            )
            retry_prompt = (
                user_prompt
                + f"\n\nPrevious output failed quality gate: {exc}\n"
                "Please fix and retry."
            )
            output = _call_claude(skill.system_prompt, retry_prompt)
            skill.quality_gate(output)  # raises if still fails

        # 6. Write Brain (best-effort)
        self._write_brain(product_id, skill_id, feature_id, output[:500])

        # 7. Touch agent last_used_at (best-effort)
        self._touch_agent(skill_id)

        return output

    # ------------------------------------------------------------------
    # Brain helpers
    # ------------------------------------------------------------------

    def _read_brain(self, product_id: str, skill_id: str) -> str:
        """GET Brain memories, return bullet-list string. Returns fallback on error."""
        import httpx  # type: ignore[import-untyped]

        try:
            base = os.getenv("API_BASE_URL", "http://localhost:8000")
            r = httpx.get(
                f"{base}/api/v1/brain/memories",
                params={
                    "scope": "product",
                    "product_id": product_id,
                    "tag": skill_id,
                    "limit": 10,
                },
                timeout=10,
            )
            if r.status_code == 200:
                memories: list[dict[str, Any]] = r.json()
                if memories:
                    return "\n".join(
                        f"- {m.get('content', '')}" for m in memories[:10]
                    )
        except Exception as exc:
            logger.warning("Brain read failed (product=%s, skill=%s): %s", product_id, skill_id, exc)
        return "(no prior memories)"

    def _write_brain(
        self,
        product_id: str,
        skill_id: str,
        feature_id: str,
        summary: str,
    ) -> None:
        """POST output summary to Brain. Best-effort — swallows all exceptions."""
        import httpx  # type: ignore[import-untyped]

        try:
            base = os.getenv("API_BASE_URL", "http://localhost:8000")
            httpx.post(
                f"{base}/api/v1/brain/memories",
                json={
                    "scope": "product",
                    "product_id": product_id,
                    "tag": skill_id,
                    "content": (
                        f"[{skill_id}] feature={feature_id}: {summary}"
                    ),
                },
                timeout=10,
            )
        except Exception as exc:
            logger.warning("Brain write failed (product=%s, skill=%s): %s", product_id, skill_id, exc)

    # ------------------------------------------------------------------
    # Agent touch helper
    # ------------------------------------------------------------------

    def _touch_agent(self, skill_id: str) -> None:
        """UPDATE agents SET last_used_at=now() for agents matching skill_id.
        Uses sync SQLAlchemy engine. Best-effort — swallows all exceptions.
        """
        try:
            from sqlalchemy import create_engine, text

            raw_url = os.getenv(
                "DATABASE_URL",
                "postgresql+asyncpg://postgres:postgres@localhost:5432/projectzero",
            )
            # Convert async driver to sync (asyncpg → psycopg2 or pg8000)
            sync_url = (
                raw_url
                .replace("postgresql+asyncpg://", "postgresql+psycopg2://")
                .replace("postgresql+aiosqlite://", "sqlite:///")
            )
            # If still async scheme, fall back to plain postgresql://
            if "+async" in sync_url or "aio" in sync_url:
                sync_url = sync_url.replace("+asyncpg", "").replace("+aiosqlite", "")

            prefix = skill_id[:4]
            engine = create_engine(sync_url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        UPDATE agents
                           SET last_used_at = now()
                         WHERE agent_id LIKE :prefix_pat
                            OR skills @> :skill_arr ::jsonb
                        """
                    ),
                    {
                        "prefix_pat": f"%-{prefix}%",
                        "skill_arr": f'["{skill_id}"]',
                    },
                )
                conn.commit()
        except Exception as exc:
            logger.warning("_touch_agent failed (skill=%s): %s", skill_id, exc)
