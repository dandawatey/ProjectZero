"""Agent seeder — PRJ0-49.

Idempotent upsert of core factory agents on startup.
Uses select-then-insert pattern to avoid dialect-specific ON CONFLICT syntax.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent

logger = logging.getLogger(__name__)

CORE_AGENTS = [
    {
        "agent_id": "spec-agent",
        "name": "Spec Agent",
        "skills": ["spec", "requirements"],
        "model": "claude-sonnet-4-6",
        "status": "active",
    },
    {
        "agent_id": "arch-agent",
        "name": "Architecture Agent",
        "skills": ["arch", "adr", "design"],
        "model": "claude-sonnet-4-6",
        "status": "active",
    },
    {
        "agent_id": "impl-agent",
        "name": "Implementation Agent",
        "skills": ["implement", "tdd", "coding"],
        "model": "claude-sonnet-4-6",
        "status": "active",
    },
    {
        "agent_id": "review-agent",
        "name": "Review Agent",
        "skills": ["review", "quality-gate"],
        "model": "claude-sonnet-4-6",
        "status": "active",
    },
    {
        "agent_id": "deploy-agent",
        "name": "Deploy Agent",
        "skills": ["deploy", "release", "changelog"],
        "model": "claude-sonnet-4-6",
        "status": "active",
    },
]


async def seed_agents(db: AsyncSession) -> None:
    """Upsert core agents. Idempotent — safe to call on every startup."""
    for data in CORE_AGENTS:
        result = await db.execute(
            select(Agent).where(Agent.agent_id == data["agent_id"])
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            agent = Agent(**data)
            db.add(agent)
            logger.info("Seeded agent: %s", data["agent_id"])
        else:
            logger.debug("Agent already exists, skipping: %s", data["agent_id"])

    await db.commit()
    logger.info("Agent seeding complete.")
