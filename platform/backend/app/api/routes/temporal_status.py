"""Temporal execution visibility — real-time workflow status from Temporal server."""

from fastapi import APIRouter
from app.temporal_integration.client import get_temporal_client
import os

router = APIRouter()


@router.get("/workers")
async def list_workers():
    """List active Temporal workers and their task queues."""
    try:
        client = await get_temporal_client()
        # Worker info from task queue
        task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "projectzero-factory")
        return {
            "task_queue": task_queue,
            "status": "connected",
            "host": os.getenv("TEMPORAL_HOST", "localhost:7233"),
            "namespace": os.getenv("TEMPORAL_NAMESPACE", "default"),
        }
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}


@router.get("/running")
async def list_running_workflows():
    """List all currently running workflows from Temporal."""
    try:
        client = await get_temporal_client()
        workflows = []
        async for wf in client.list_workflows('ExecutionStatus = "Running"'):
            workflows.append({
                "workflow_id": wf.id,
                "run_id": wf.run_id,
                "type": wf.workflow_type,
                "status": wf.status.name if wf.status else "RUNNING",
                "start_time": wf.start_time.isoformat() if wf.start_time else None,
            })
        return {"count": len(workflows), "workflows": workflows}
    except Exception as e:
        return {"status": "error", "error": str(e), "workflows": []}


@router.get("/completed")
async def list_completed_workflows():
    """List recently completed workflows."""
    try:
        client = await get_temporal_client()
        workflows = []
        async for wf in client.list_workflows(
            'ExecutionStatus = "Completed" ORDER BY StartTime DESC LIMIT 50'
        ):
            workflows.append({
                "workflow_id": wf.id,
                "run_id": wf.run_id,
                "type": wf.workflow_type,
                "status": "COMPLETED",
                "start_time": wf.start_time.isoformat() if wf.start_time else None,
                "close_time": wf.close_time.isoformat() if wf.close_time else None,
            })
        return {"count": len(workflows), "workflows": workflows}
    except Exception as e:
        return {"status": "error", "error": str(e), "workflows": []}


@router.get("/failed")
async def list_failed_workflows():
    """List failed workflows."""
    try:
        client = await get_temporal_client()
        workflows = []
        async for wf in client.list_workflows(
            'ExecutionStatus = "Failed" ORDER BY StartTime DESC LIMIT 50'
        ):
            workflows.append({
                "workflow_id": wf.id,
                "run_id": wf.run_id,
                "type": wf.workflow_type,
                "status": "FAILED",
                "start_time": wf.start_time.isoformat() if wf.start_time else None,
            })
        return {"count": len(workflows), "workflows": workflows}
    except Exception as e:
        return {"status": "error", "error": str(e), "workflows": []}


@router.get("/workflow/{workflow_id}")
async def get_workflow_execution(workflow_id: str):
    """Get detailed execution history for a specific workflow."""
    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()

        # Get history events
        events = []
        async for event in handle.fetch_history_events():
            events.append({
                "event_id": event.event_id,
                "event_type": event.event_type.name if event.event_type else str(event.event_type),
                "timestamp": event.event_time.isoformat() if event.event_time else None,
            })

        return {
            "workflow_id": workflow_id,
            "run_id": desc.run_id,
            "type": desc.workflow_type,
            "status": desc.status.name if desc.status else "UNKNOWN",
            "start_time": desc.start_time.isoformat() if desc.start_time else None,
            "close_time": desc.close_time.isoformat() if desc.close_time else None,
            "task_queue": desc.task_queue,
            "history_length": desc.history_length,
            "events": events[:100],  # cap at 100 events
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/workflow/{workflow_id}/signal/{signal_name}")
async def send_signal(workflow_id: str, signal_name: str, body: dict = {}):
    """Send a signal to a running workflow (e.g., approve, unblock)."""
    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)
        await handle.signal(signal_name, body.get("payload"))
        return {"status": "signal_sent", "workflow_id": workflow_id, "signal": signal_name}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/workflow/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str):
    """Cancel a running workflow."""
    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)
        await handle.cancel()
        return {"status": "cancelled", "workflow_id": workflow_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/workflow/{workflow_id}/query/{query_name}")
async def query_workflow(workflow_id: str, query_name: str):
    """Query a running workflow (e.g., current_stage, is_blocked)."""
    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)
        result = await handle.query(query_name)
        return {"workflow_id": workflow_id, "query": query_name, "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}
