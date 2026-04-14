"""ProductBootstrapWorkflow — one-shot product setup.

Steps (all auto, no human gate):
  1. bootstrap_prd_activity       → Claude generates PRD from brief
  2. bootstrap_jira_activity      → JIRA project + initial epic
  3. bootstrap_confluence_activity → Confluence home page
  4. bootstrap_db_activity        → DB product record + Brain seed

All steps run; failures are logged but don't block subsequent steps.
Returns full status map so caller sees exactly what succeeded.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.temporal_integration.bootstrap_activities import (
        BootstrapInput,
        bootstrap_prd_activity,
        bootstrap_jira_activity,
        bootstrap_confluence_activity,
        bootstrap_db_activity,
    )

logger = logging.getLogger(__name__)

_RETRY = RetryPolicy(maximum_attempts=2, initial_interval=timedelta(seconds=5))
_TIMEOUT = timedelta(minutes=5)


@dataclass
class ProductBootstrapInput:
    workflow_run_id: str
    product_id: str
    product_name: str
    description: str
    owner_email: str
    repo_path: str
    jira_project_key: str


@workflow.defn(name="ProductBootstrapWorkflow")
class ProductBootstrapWorkflow:
    """Bootstrap a new product end-to-end. No human gates — fully automated."""

    def __init__(self) -> None:
        self._stage = "starting"

    @workflow.query
    def current_stage(self) -> str:
        return self._stage

    @workflow.run
    async def run(self, inp: ProductBootstrapInput) -> dict:
        base = BootstrapInput(
            workflow_run_id=inp.workflow_run_id,
            product_id=inp.product_id,
            product_name=inp.product_name,
            description=inp.description,
            owner_email=inp.owner_email,
            repo_path=inp.repo_path,
            jira_project_key=inp.jira_project_key,
        )
        results = {}

        # 1. PRD
        self._stage = "generating_prd"
        results["prd"] = await workflow.execute_activity(
            bootstrap_prd_activity, base,
            start_to_close_timeout=_TIMEOUT, retry_policy=_RETRY)

        # 2. JIRA (parallel-safe — no dependency on PRD output)
        self._stage = "creating_jira"
        results["jira"] = await workflow.execute_activity(
            bootstrap_jira_activity, base,
            start_to_close_timeout=_TIMEOUT, retry_policy=_RETRY)

        # 3. Confluence
        self._stage = "creating_confluence"
        results["confluence"] = await workflow.execute_activity(
            bootstrap_confluence_activity, base,
            start_to_close_timeout=_TIMEOUT, retry_policy=_RETRY)

        # 4. DB
        self._stage = "seeding_db"
        results["db"] = await workflow.execute_activity(
            bootstrap_db_activity, base,
            start_to_close_timeout=_TIMEOUT, retry_policy=_RETRY)

        self._stage = "completed"
        ok_count = sum(1 for v in results.values() if v.get("status") == "ok")

        return {
            "status": "completed",
            "workflow": "ProductBootstrapWorkflow",
            "product_id": inp.product_id,
            "product_name": inp.product_name,
            "steps_ok": ok_count,
            "steps_total": 4,
            "results": results,
        }
