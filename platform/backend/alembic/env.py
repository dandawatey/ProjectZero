"""Alembic env.py — async SQLAlchemy engine, all models imported for autogenerate.

PRJ0-4: initial Alembic migration setup.
"""

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Import Base and ALL models so autogenerate can detect every table.
# ---------------------------------------------------------------------------
from app.core.database import Base  # noqa: F401

# workflow models
from app.models.workflow import (  # noqa: F401
    WorkflowRun,
    WorkflowStep,
    WorkflowApproval,
    WorkflowArtifact,
    WorkflowAudit,
    WorkflowTrigger,
    AgentContribution,
)

# user / auth models
from app.models.user import User, RefreshToken  # noqa: F401

# brain models
from app.models.brain import Memory, Decision, Pattern, Conversation  # noqa: F401

# activity models
from app.models.activity import UserActivity, UserSession, SystemEvent  # noqa: F401

# metrics model
from app.models.metrics import CxoMetricsCache  # noqa: F401

# product model
from app.models.product import Product  # noqa: F401

# ---------------------------------------------------------------------------
# Alembic config
# ---------------------------------------------------------------------------
config = context.config

# Override sqlalchemy.url from DATABASE_URL env var if present (12-factor).
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline mode — generate SQL without live DB connection
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — async engine
# ---------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
