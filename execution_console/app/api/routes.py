"""FastAPI routes for Execution Console — PRJ0-56."""
from __future__ import annotations
from fastapi import APIRouter
from ..models.events import ExecutionEvent, StatusSnapshot
from ..services import event_store, state_engine

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
