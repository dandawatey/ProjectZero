"""Temporal worker.

Registers 8 core workflows + all activities.
Started as asyncio task in FastAPI lifespan (non-blocking).
Graceful shutdown on app stop.

Task queue: settings.temporal_task_queue (default: 'projectzero-factory')
"""

from __future__ import annotations

import asyncio
import logging

from temporalio.worker import Worker

from app.temporal_integration.client import get_temporal_client
from app.temporal_integration.workflows import FeatureDevelopmentWorkflow
from app.temporal_integration.factory_workflow import FactorySelfBuildWorkflow
from app.temporal_integration.bug_workflow import BugFixWorkflow
from app.temporal_integration.task_workflow import TaskWorkflow
from app.temporal_integration.epic_workflow import EpicOrchestratorWorkflow
from app.temporal_integration.ticket_router_workflow import TicketRouterWorkflow
from app.temporal_integration.activities import (
    spec_activity,
    arch_activity,
    impl_activity,
    review_activity,
    deploy_activity,
)
from app.temporal_integration.factory_activities import (
    factory_spec_activity,
    factory_arch_activity,
    factory_impl_activity,
    factory_review_activity,
    factory_deploy_activity,
)
from app.temporal_integration.bug_activities import (
    diagnose_activity,
    bugfix_activity,
    verify_activity,
)
from app.temporal_integration.task_activities import (
    task_impl_activity,
    task_review_activity,
)
from app.temporal_integration.classifier_activity import classify_ticket_activity
from app.temporal_integration.product_bootstrap_workflow import ProductBootstrapWorkflow
from app.temporal_integration.release_workflow import ReleaseWorkflow
from app.temporal_integration.release_activities import (
    verify_release_activity,
    generate_changelog_activity,
    publish_release_activity,
    notify_release_activity,
)
from app.temporal_integration.bootstrap_activities import (
    bootstrap_prd_activity,
    bootstrap_jira_activity,
    bootstrap_confluence_activity,
    bootstrap_db_activity,
)
from app.temporal_integration.mcra_workflow import MCRAWorkflow
from app.temporal_integration.mcra_activities import (
    mcra_checker_activity,
    mcra_reviewer_activity,
    mcra_notify_activity,
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_worker_task: asyncio.Task | None = None


async def start_worker() -> None:
    """Start Temporal worker as background asyncio task."""
    global _worker_task
    settings = get_settings()

    try:
        client = await get_temporal_client()
    except Exception as exc:
        logger.warning("Temporal unavailable — worker not started: %s", exc)
        return

    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[
            # Ticket routing
            TicketRouterWorkflow,
            # Development
            FeatureDevelopmentWorkflow,
            BugFixWorkflow,
            TaskWorkflow,
            EpicOrchestratorWorkflow,
            # Factory dogfood
            FactorySelfBuildWorkflow,
            # Product lifecycle
            ProductBootstrapWorkflow,
            ReleaseWorkflow,
            # MCRA 4-eye governance (PRJ0-37)
            MCRAWorkflow,
        ],
        activities=[
            # Story activities
            spec_activity, arch_activity, impl_activity, review_activity, deploy_activity,
            # Factory activities
            factory_spec_activity, factory_arch_activity, factory_impl_activity,
            factory_review_activity, factory_deploy_activity,
            # Bug activities
            diagnose_activity, bugfix_activity, verify_activity,
            # Task activities
            task_impl_activity, task_review_activity,
            # Classifier
            classify_ticket_activity,
            # Bootstrap activities
            bootstrap_prd_activity, bootstrap_jira_activity,
            bootstrap_confluence_activity, bootstrap_db_activity,
            # Release activities
            verify_release_activity, generate_changelog_activity,
            publish_release_activity, notify_release_activity,
            # MCRA activities (PRJ0-37)
            mcra_checker_activity, mcra_reviewer_activity, mcra_notify_activity,
        ],
    )

    async def _run() -> None:
        logger.info(
            "Temporal worker started — task_queue=%s namespace=%s",
            settings.temporal_task_queue,
            settings.temporal_namespace,
        )
        try:
            await worker.run()
        except asyncio.CancelledError:
            logger.info("Temporal worker shutting down")
            raise
        except Exception as exc:
            logger.error("Temporal worker crashed: %s", exc)

    _worker_task = asyncio.create_task(_run(), name="temporal-worker")


async def stop_worker() -> None:
    """Cancel worker task on app shutdown."""
    global _worker_task
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    _worker_task = None
