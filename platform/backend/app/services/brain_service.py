"""ProjectZero Brain service — persistent memory, decisions, patterns, conversations."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brain import Memory, Decision, Pattern, Conversation


# ── MEMORY ──────────────────────────────────────

async def store_memory(
    db: AsyncSession, *, scope: str, category: str, title: str, content: str,
    product_id: Optional[str] = None, tags: list[str] = [],
    source_agent: Optional[str] = None, source_workflow: Optional[str] = None,
    source_stage: Optional[str] = None, confidence: float = 0.8,
    promotion_status: str = "local",
) -> Memory:
    memory = Memory(
        scope=scope, product_id=product_id, category=category,
        title=title, content=content, tags=tags,
        source_agent=source_agent, source_workflow=source_workflow,
        source_stage=source_stage, confidence=confidence,
        promotion_status=promotion_status,
    )
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    return memory


async def recall_memories(
    db: AsyncSession, *, scope: Optional[str] = None, category: Optional[str] = None,
    product_id: Optional[str] = None, tags: Optional[list[str]] = None,
    search: Optional[str] = None, limit: int = 20,
) -> list[Memory]:
    query = select(Memory).where(Memory.is_active == True).order_by(desc(Memory.updated_at))
    if scope:
        query = query.where(Memory.scope == scope)
    if category:
        query = query.where(Memory.category == category)
    if product_id:
        query = query.where(or_(Memory.product_id == product_id, Memory.scope == "factory"))
    if tags:
        query = query.where(Memory.tags.overlap(tags))
    if search:
        query = query.where(or_(
            Memory.title.ilike(f"%{search}%"),
            Memory.content.ilike(f"%{search}%"),
        ))
    result = await db.execute(query.limit(limit))
    memories = list(result.scalars().all())
    # Bump usage count
    for m in memories:
        m.usage_count += 1
        m.last_used_at = datetime.utcnow()
    await db.commit()
    return memories


async def promote_memory(db: AsyncSession, memory_id: UUID) -> Memory:
    memory = await db.get(Memory, memory_id)
    if not memory:
        raise ValueError(f"Memory {memory_id} not found")
    promoted = Memory(
        scope="factory", category=memory.category, title=memory.title,
        content=memory.content, tags=memory.tags,
        source_agent=memory.source_agent, confidence=memory.confidence,
        is_promoted=True, promoted_from=memory.id,
    )
    db.add(promoted)
    await db.commit()
    await db.refresh(promoted)
    return promoted


# ── DECISIONS ───────────────────────────────────

async def record_decision(
    db: AsyncSession, *, title: str, context: str, options: list[dict],
    chosen: str, rationale: str, decided_by: str,
    product_id: Optional[str] = None, tags: list[str] = [],
) -> Decision:
    decision = Decision(
        product_id=product_id, title=title, context=context,
        options=options, chosen=chosen, rationale=rationale,
        decided_by=decided_by, tags=tags,
    )
    db.add(decision)
    await db.commit()
    await db.refresh(decision)
    return decision


async def get_decisions(
    db: AsyncSession, product_id: Optional[str] = None, limit: int = 50,
) -> list[Decision]:
    query = select(Decision).order_by(desc(Decision.decided_at))
    if product_id:
        query = query.where(Decision.product_id == product_id)
    result = await db.execute(query.limit(limit))
    return list(result.scalars().all())


# ── PATTERNS ────────────────────────────────────

async def store_pattern(
    db: AsyncSession, *, scope: str, category: str, title: str,
    problem: str, solution: str, example: Optional[str] = None,
    anti_pattern: Optional[str] = None,
) -> Pattern:
    pattern = Pattern(
        scope=scope, category=category, title=title,
        problem=problem, solution=solution, example=example,
        anti_pattern=anti_pattern,
    )
    db.add(pattern)
    await db.commit()
    await db.refresh(pattern)
    return pattern


async def get_patterns(
    db: AsyncSession, *, category: Optional[str] = None,
    scope: Optional[str] = None, limit: int = 50,
) -> list[Pattern]:
    query = select(Pattern).order_by(desc(Pattern.times_used))
    if category:
        query = query.where(Pattern.category == category)
    if scope:
        query = query.where(Pattern.scope == scope)
    result = await db.execute(query.limit(limit))
    return list(result.scalars().all())


# ── CONVERSATIONS ───────────────────────────────

async def create_conversation(
    db: AsyncSession, *, product_id: str, mode: str,
    workflow_run_id: Optional[UUID] = None, stage: Optional[str] = None,
) -> Conversation:
    convo = Conversation(
        product_id=product_id, mode=mode,
        workflow_run_id=workflow_run_id, stage=stage,
        messages=[],
    )
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return convo


async def add_message(
    db: AsyncSession, conversation_id: UUID, role: str, content: str,
) -> Conversation:
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        raise ValueError(f"Conversation {conversation_id} not found")
    msgs = list(convo.messages or [])
    msgs.append({"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()})
    convo.messages = msgs
    convo.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(convo)
    return convo


async def get_conversations(
    db: AsyncSession, product_id: str,
    workflow_run_id: Optional[UUID] = None, mode: Optional[str] = None,
    limit: int = 20,
) -> list[Conversation]:
    query = select(Conversation).where(Conversation.product_id == product_id).order_by(desc(Conversation.updated_at))
    if workflow_run_id:
        query = query.where(Conversation.workflow_run_id == workflow_run_id)
    if mode:
        query = query.where(Conversation.mode == mode)
    result = await db.execute(query.limit(limit))
    return list(result.scalars().all())
