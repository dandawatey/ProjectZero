"""Brain API — persistent memory, decisions, patterns, conversations."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import brain_service

router = APIRouter()


# ── MEMORY ──────────────────────────────────────

@router.post("/memory")
async def store_memory(body: dict, db: AsyncSession = Depends(get_db)):
    m = await brain_service.store_memory(
        db, scope=body["scope"], category=body["category"],
        title=body["title"], content=body["content"],
        product_id=body.get("product_id"), tags=body.get("tags", []),
        source_agent=body.get("source_agent"), source_workflow=body.get("source_workflow"),
        source_stage=body.get("source_stage"), confidence=body.get("confidence", 0.8),
    )
    return {"id": str(m.id), "status": "stored"}


@router.get("/memory")
async def recall_memories(
    scope: Optional[str] = None, category: Optional[str] = None,
    product_id: Optional[str] = None, search: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
):
    memories = await brain_service.recall_memories(
        db, scope=scope, category=category, product_id=product_id, search=search, limit=limit,
    )
    return [
        {"id": str(m.id), "scope": m.scope, "category": m.category, "title": m.title,
         "content": m.content, "tags": m.tags, "confidence": m.confidence,
         "usage_count": m.usage_count, "source_agent": m.source_agent,
         "created_at": m.created_at.isoformat()}
        for m in memories
    ]


@router.post("/memory/{memory_id}/promote")
async def promote_memory(memory_id: UUID, db: AsyncSession = Depends(get_db)):
    promoted = await brain_service.promote_memory(db, memory_id)
    return {"id": str(promoted.id), "status": "promoted", "scope": "factory"}


# ── DECISIONS ───────────────────────────────────

@router.post("/decisions")
async def record_decision(body: dict, db: AsyncSession = Depends(get_db)):
    d = await brain_service.record_decision(
        db, title=body["title"], context=body["context"],
        options=body["options"], chosen=body["chosen"],
        rationale=body["rationale"], decided_by=body["decided_by"],
        product_id=body.get("product_id"), tags=body.get("tags", []),
    )
    return {"id": str(d.id), "status": "recorded"}


@router.get("/decisions")
async def list_decisions(
    product_id: Optional[str] = None, limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    decisions = await brain_service.get_decisions(db, product_id=product_id, limit=limit)
    return [
        {"id": str(d.id), "title": d.title, "chosen": d.chosen, "rationale": d.rationale,
         "decided_by": d.decided_by, "status": d.status, "decided_at": d.decided_at.isoformat()}
        for d in decisions
    ]


# ── PATTERNS ────────────────────────────────────

@router.post("/patterns")
async def store_pattern(body: dict, db: AsyncSession = Depends(get_db)):
    p = await brain_service.store_pattern(
        db, scope=body["scope"], category=body["category"],
        title=body["title"], problem=body["problem"], solution=body["solution"],
        example=body.get("example"), anti_pattern=body.get("anti_pattern"),
    )
    return {"id": str(p.id), "status": "stored"}


@router.get("/patterns")
async def list_patterns(
    category: Optional[str] = None, scope: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    patterns = await brain_service.get_patterns(db, category=category, scope=scope, limit=limit)
    return [
        {"id": str(p.id), "scope": p.scope, "category": p.category, "title": p.title,
         "problem": p.problem, "solution": p.solution, "times_used": p.times_used,
         "status": p.status, "success_rate": p.success_rate}
        for p in patterns
    ]


# ── CONVERSATIONS ───────────────────────────────

@router.post("/conversations")
async def create_conversation(body: dict, db: AsyncSession = Depends(get_db)):
    c = await brain_service.create_conversation(
        db, product_id=body["product_id"], mode=body["mode"],
        workflow_run_id=UUID(body["workflow_run_id"]) if body.get("workflow_run_id") else None,
        stage=body.get("stage"),
    )
    return {"id": str(c.id), "mode": c.mode, "status": "created"}


@router.post("/conversations/{conversation_id}/message")
async def add_message(conversation_id: UUID, body: dict, db: AsyncSession = Depends(get_db)):
    c = await brain_service.add_message(db, conversation_id, body["role"], body["content"])
    return {"id": str(c.id), "message_count": len(c.messages)}


@router.get("/conversations")
async def list_conversations(
    product_id: str, workflow_run_id: Optional[str] = None,
    mode: Optional[str] = None, limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
):
    wf_id = UUID(workflow_run_id) if workflow_run_id else None
    convos = await brain_service.get_conversations(
        db, product_id=product_id, workflow_run_id=wf_id, mode=mode, limit=limit,
    )
    return [
        {"id": str(c.id), "mode": c.mode, "stage": c.stage,
         "message_count": len(c.messages or []),
         "is_active": c.is_active, "updated_at": c.updated_at.isoformat()}
        for c in convos
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: UUID, db: AsyncSession = Depends(get_db)):
    c = await db.get(Conversation, conversation_id)
    if not c:
        return {"error": "Not found"}
    return {
        "id": str(c.id), "mode": c.mode, "stage": c.stage,
        "product_id": c.product_id, "messages": c.messages,
        "summary": c.summary, "decisions_made": c.decisions_made,
        "action_items": c.action_items, "is_active": c.is_active,
    }
