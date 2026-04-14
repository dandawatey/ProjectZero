"""AgentDispatcher — PRJ0-51 / PRJ0-53.

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
  8. Log execution start/finish to agent_executions table (PRJ0-53)
  9. Post JIRA comment on ticket (PRJ0-53)
"""

from __future__ import annotations

import logging
import os
import time
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
        ticket_id: str = "",
        workflow_run_id: str = "",
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

        # PRJ0-53: start execution log
        exec_id = self._log_start(skill_id, ticket_id, workflow_run_id)
        t0 = time.time()
        retried = False
        brain_ok = False
        qg_passed = False

        try:
            # 4. Call Claude
            output = _call_claude(skill.system_prompt, user_prompt)

            # 5. Quality gate — retry once on failure
            try:
                skill.quality_gate(output)
                qg_passed = True
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
                qg_passed = True
                retried = True

            # 6. Write Brain (best-effort) — pass qg_passed for promotion auto-flag (PRJ0-38)
            self._write_brain(product_id, skill_id, feature_id, output[:500], quality_gate_passed=qg_passed)
            brain_ok = True

            # 7. Touch agent last_used_at (best-effort)
            self._touch_agent(skill_id)

            # PRJ0-53: log finish (success)
            duration_ms = int((time.time() - t0) * 1000)
            final_status = "retried" if retried else "ok"
            self._log_finish(exec_id, final_status, duration_ms, qg_passed, brain_ok)
            self._jira_comment(ticket_id, skill_id, final_status, duration_ms, qg_passed)

            return output

        except Exception as exc:
            # PRJ0-53: log finish (failure)
            self._log_finish(
                exec_id, "failed", int((time.time() - t0) * 1000), False, False, str(exc)
            )
            raise

    # ------------------------------------------------------------------
    # PRJ0-53: Execution logging helpers
    # ------------------------------------------------------------------

    def _get_sync_engine(self):
        """Build a sync SQLAlchemy engine from DATABASE_URL env var."""
        from sqlalchemy import create_engine

        raw_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/projectzero",
        )
        sync_url = (
            raw_url
            .replace("postgresql+asyncpg://", "postgresql+psycopg2://")
            .replace("postgresql+aiosqlite://", "sqlite:///")
        )
        if "+async" in sync_url or "aio" in sync_url:
            sync_url = sync_url.replace("+asyncpg", "").replace("+aiosqlite", "")
        return create_engine(sync_url, pool_pre_ping=True)

    def _log_start(self, skill_id: str, ticket_id: str, workflow_run_id: str) -> str:
        """Insert AgentExecution row with status='running'. Returns exec id or '' on error."""
        try:
            import uuid as _uuid
            from sqlalchemy import text

            exec_id = str(_uuid.uuid4())
            engine = self._get_sync_engine()
            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        INSERT INTO agent_executions
                            (id, agent_id, skill_id, ticket_id, workflow_run_id, status, brain_written)
                        VALUES
                            (:id, :agent_id, :skill_id, :ticket_id, :workflow_run_id, 'running', false)
                        """
                    ),
                    {
                        "id": exec_id,
                        "agent_id": f"agent-{skill_id}",
                        "skill_id": skill_id,
                        "ticket_id": ticket_id or None,
                        "workflow_run_id": workflow_run_id or None,
                    },
                )
                conn.commit()
            return exec_id
        except Exception as exc:
            logger.warning("_log_start failed (skill=%s): %s", skill_id, exc)
            return ""

    def _log_finish(
        self,
        exec_id: str,
        status: str,
        duration_ms: int,
        quality_gate_passed: bool,
        brain_written: bool,
        error: str | None = None,
    ) -> None:
        """UPDATE agent_executions with completion data. Swallows all exceptions."""
        if not exec_id:
            return
        try:
            from sqlalchemy import text

            engine = self._get_sync_engine()
            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        UPDATE agent_executions
                           SET completed_at = now(),
                               status = :status,
                               duration_ms = :duration_ms,
                               quality_gate_passed = :quality_gate_passed,
                               brain_written = :brain_written,
                               error_message = :error_message
                         WHERE id = :id
                        """
                    ),
                    {
                        "id": exec_id,
                        "status": status,
                        "duration_ms": duration_ms,
                        "quality_gate_passed": quality_gate_passed,
                        "brain_written": brain_written,
                        "error_message": error[:1000] if error else None,
                    },
                )
                conn.commit()
        except Exception as exc:
            logger.warning("_log_finish failed (exec_id=%s): %s", exec_id, exc)

    def _jira_comment(
        self,
        ticket_id: str,
        skill_id: str,
        status: str,
        duration_ms: int,
        quality_gate_passed: bool,
    ) -> None:
        """POST completion comment to JIRA ticket. Swallows all exceptions."""
        if not ticket_id:
            return
        jira_base = os.getenv("JIRA_BASE_URL", "")
        jira_email = os.getenv("JIRA_USER_EMAIL", "")
        jira_token = os.getenv("JIRA_API_TOKEN", "")
        if not (jira_base and jira_email and jira_token):
            return
        try:
            import httpx  # type: ignore[import-untyped]

            gate_str = "passed" if quality_gate_passed else "failed"
            duration_s = duration_ms // 1000
            body = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        f"[ProjectZero Agent] {skill_id} stage completed. "
                                        f"Status: {status}. "
                                        f"Duration: {duration_s}s. "
                                        f"Quality gate: {gate_str}."
                                    ),
                                }
                            ],
                        }
                    ],
                }
            }
            with httpx.Client(timeout=10) as client:
                client.post(
                    f"{jira_base}/rest/api/3/issue/{ticket_id}/comment",
                    auth=(jira_email, jira_token),
                    json=body,
                )
        except Exception as exc:
            logger.warning("_jira_comment failed (ticket=%s, skill=%s): %s", ticket_id, skill_id, exc)

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
        quality_gate_passed: bool = False,
    ) -> None:
        """POST output summary to Brain. Best-effort — swallows all exceptions.

        PRJ0-38: Auto-flags spec/arch memories as pending promotion when quality gate passes.
        """
        import httpx  # type: ignore[import-untyped]

        try:
            base = os.getenv("API_BASE_URL", "http://localhost:8000")
            # PRJ0-38: pattern-worthy skills → pending promotion when QG passes
            promotion_status = "local"
            if quality_gate_passed and skill_id in ("spec", "arch"):
                promotion_status = "pending"
            httpx.post(
                f"{base}/api/v1/brain/memories",
                json={
                    "scope": "product",
                    "product_id": product_id,
                    "tag": skill_id,
                    "content": (
                        f"[{skill_id}] feature={feature_id}: {summary}"
                    ),
                    "promotion_status": promotion_status,
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
            from sqlalchemy import text

            prefix = skill_id[:4]
            engine = self._get_sync_engine()
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
