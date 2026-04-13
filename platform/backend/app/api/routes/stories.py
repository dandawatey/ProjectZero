from __future__ import annotations

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.story import Story, AcceptanceCriteria
from app.schemas.story import StoryCreate, StoryRead, StoryUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=StoryRead, status_code=201)
async def create_story(body: StoryCreate, db: AsyncSession = Depends(get_db)):
    story = Story(
        id=uuid.uuid4(),
        workflow_run_id=body.workflow_run_id,
        feature_id=body.feature_id,
        title=body.title,
        role=body.role,
        action=body.action,
        benefit=body.benefit,
        priority=body.priority,
        status="draft",
    )
    db.add(story)
    await db.flush()  # get story.id before inserting criteria

    for ac in body.criteria:
        db.add(AcceptanceCriteria(
            id=uuid.uuid4(),
            story_id=story.id,
            given=ac.given,
            when_=ac.when_,
            then_=ac.then_,
            order=ac.order,
        ))

    await db.commit()

    # Re-fetch with criteria eagerly loaded
    result = await db.execute(
        select(Story).options(selectinload(Story.criteria)).where(Story.id == story.id)
    )
    return StoryRead.model_validate(result.scalar_one())


@router.get("/", response_model=list[StoryRead])
async def list_stories(
    workflow_run_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Story)
        .options(selectinload(Story.criteria))
        .where(Story.workflow_run_id == workflow_run_id)
        .order_by(Story.priority.desc(), Story.created_at)
    )
    stories = result.scalars().all()
    return [StoryRead.model_validate(s) for s in stories]


@router.patch("/{story_id}", response_model=StoryRead)
async def update_story_status(
    story_id: uuid.UUID,
    body: StoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Story).options(selectinload(Story.criteria)).where(Story.id == story_id)
    )
    story = result.scalar_one_or_none()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    allowed = {"draft", "approved", "rejected"}
    if body.status not in allowed:
        raise HTTPException(status_code=422, detail=f"status must be one of {allowed}")

    story.status = body.status
    await db.commit()
    await db.refresh(story)

    # Re-fetch to ensure criteria loaded after refresh
    result = await db.execute(
        select(Story).options(selectinload(Story.criteria)).where(Story.id == story_id)
    )
    return StoryRead.model_validate(result.scalar_one())
