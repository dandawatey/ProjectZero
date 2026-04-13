from __future__ import annotations

import logging
from typing import Any

from temporalio.client import Client

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_client: Client | None = None


async def get_temporal_client() -> Client:
    """Return a cached Temporal client, connecting lazily."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = await Client.connect(
            settings.temporal_host,
            namespace=settings.temporal_namespace,
        )
    return _client


async def start_workflow(
    workflow_name: str,
    workflow_id: str,
    args: list[Any] | None = None,
    task_queue: str | None = None,
) -> str:
    """Start a Temporal workflow and return its run ID."""
    settings = get_settings()
    client = await get_temporal_client()
    handle = await client.start_workflow(
        workflow_name,
        args[0] if args and len(args) == 1 else (args or []),
        id=workflow_id,
        task_queue=task_queue or settings.temporal_task_queue,
    )
    logger.info("Started Temporal workflow %s with run_id=%s", workflow_id, handle.result_run_id)
    return handle.result_run_id


async def signal_workflow(
    workflow_id: str,
    signal_name: str,
    payload: Any = None,
) -> None:
    """Send a signal to a running Temporal workflow."""
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(signal_name, payload)
    logger.info("Sent signal '%s' to workflow %s", signal_name, workflow_id)


async def query_workflow(
    workflow_id: str,
    query_name: str,
) -> Any:
    """Query a running Temporal workflow."""
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    result = await handle.query(query_name)
    return result


async def cancel_workflow(workflow_id: str) -> None:
    """Request cancellation of a Temporal workflow."""
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    await handle.cancel()
    logger.info("Cancelled workflow %s", workflow_id)
