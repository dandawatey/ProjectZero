"""FastAPI routes for Execution Console — PRJ0-56, PRJ0-74, PRJ0-75."""
from __future__ import annotations
from fastapi import APIRouter
from ..models.events import ExecutionEvent, StatusSnapshot
from ..services import event_store, state_engine
from ..integrations.claude import mem_search as _mem_search

router = APIRouter()


@router.post("/events", status_code=201)
async def ingest_event(event: ExecutionEvent) -> dict:
    """Ingest execution event from Claude hooks, Temporal, or JIRA sync."""
    event_store.store_event(event)
    return {"id": event.id, "stored": True}


@router.get("/snapshot", response_model=StatusSnapshot)
async def get_snapshot() -> StatusSnapshot:
    """Current execution status snapshot with rollup."""
    return state_engine.build_snapshot()


@router.get("/events/failed")
async def get_failed_events() -> list[dict]:
    return event_store.failed_events()


@router.delete("/events")
async def clear_events() -> dict:
    event_store.clear_all()
    return {"cleared": True}


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "execution-console"}


# ---------------------------------------------------------------------------
# mem-search proxy routes — PRJ0-74
# ---------------------------------------------------------------------------

@router.get("/mem/search")
async def mem_search(q: str, limit: int = 10) -> dict:
    """Proxy to claude-mem worker — Layer 1 search."""
    import os
    port = int(os.environ.get("CLAUDE_MEM_PORT", 37777))
    resp = _mem_search.search(q, limit=limit, port=port)
    return {
        "layer": resp.layer,
        "query": resp.query,
        "total": resp.total,
        "token_cost": resp.token_cost,
        "results": [
            {
                "id": r.id,
                "snippet": r.snippet,
                "score": r.score,
                "timestamp": r.timestamp,
            }
            for r in resp.results
        ],
        "error": resp.error,
    }


@router.get("/mem/health")
async def mem_health() -> dict:
    """Check claude-mem worker status."""
    import os
    port = int(os.environ.get("CLAUDE_MEM_PORT", 37777))
    resp = _mem_search.search("health-check", limit=1, port=port)
    if resp.error:
        return {"status": "down", "message": resp.error, "port": port}
    return {"status": "ok", "port": port}


# ---------------------------------------------------------------------------
# mem-brain sync routes — PRJ0-75
# ---------------------------------------------------------------------------

@router.post("/mem/sync")
async def trigger_sync(dry_run: bool = False) -> dict:
    """Trigger claude-mem → Brain sync (PRJ0-75).

    Promotes high-value claude-mem memories (score >= threshold) to Postgres Brain.
    Use dry_run=true to preview without writing.
    """
    import os
    from ..integrations.claude.mem_bridge import MemBridge

    bridge = MemBridge(
        mem_port=int(os.environ.get("CLAUDE_MEM_PORT", 37777)),
        brain_url=os.environ.get("PROJECTZERO_BASE_URL", "http://localhost:8000"),
        brain_token=os.environ.get("PROJECTZERO_TOKEN", ""),
        threshold=float(os.environ.get("CLAUDE_MEM_BRAIN_THRESHOLD", "0.7")),
    )
    return bridge.sync(dry_run=dry_run)
