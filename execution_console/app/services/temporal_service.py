"""Temporal workflow poller — PRJ0-56."""
from __future__ import annotations
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
# Temporal Web UI base URL for links
TEMPORAL_UI_URL = os.getenv("TEMPORAL_UI_URL", "http://localhost:8233")


def fetch_running_workflows(page_size: int = 50) -> list[dict]:
    """
    Poll Temporal for running workflows via the Temporal Web API.
    Returns list of simplified workflow dicts.
    Falls back to empty list if Temporal is not reachable.
    """
    try:
        url = f"http://{TEMPORAL_HOST}/api/v1/namespaces/{TEMPORAL_NAMESPACE}/workflows"
        params = {
            "query": "ExecutionStatus='Running'",
            "pageSize": page_size,
        }
        r = httpx.get(url, params=params, timeout=5)
        r.raise_for_status()
        executions = r.json().get("executions", [])
        result = []
        for ex in executions:
            wf_id = ex.get("execution", {}).get("workflowId", "")
            run_id = ex.get("execution", {}).get("runId", "")
            result.append({
                "workflow_id": wf_id,
                "run_id": run_id,
                "workflow_type": ex.get("type", {}).get("name", ""),
                "status": ex.get("status", "Running"),
                "start_time": ex.get("startTime"),
                "close_time": ex.get("closeTime"),
                "temporal_url": f"{TEMPORAL_UI_URL}/namespaces/{TEMPORAL_NAMESPACE}/workflows/{wf_id}/{run_id}",
            })
        return result
    except Exception as exc:
        logger.debug(f"Temporal poll failed (not running?): {exc}")
        return []


def get_workflow_url(workflow_run_id: str) -> Optional[str]:
    """Build Temporal UI deep-link for a workflow run ID."""
    if not workflow_run_id:
        return None
    return f"{TEMPORAL_UI_URL}/namespaces/{TEMPORAL_NAMESPACE}/workflows/{workflow_run_id}"
