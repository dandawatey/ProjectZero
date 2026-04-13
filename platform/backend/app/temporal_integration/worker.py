"""Temporal worker — PRJ0-45.

Registers FeatureDevelopmentWorkflow + all activities.
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
from app.temporal_integration.activities import (
    spec_activity,
    arch_activity,
    impl_activity,
    review_activity,
    deploy_activity,
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
        workflows=[FeatureDevelopmentWorkflow],
        activities=[
            spec_activity,
            arch_activity,
            impl_activity,
            review_activity,
            deploy_activity,
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
