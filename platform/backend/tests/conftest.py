"""Pytest fixtures for ProjectZero backend test suite — PRJ0-64."""
import asyncio
import os

# Set env vars BEFORE any app imports so database.py and config.py pick them up
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-32-chars-minimum!!")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("JIRA_BASE_URL", "https://mock-jira.example.com")
os.environ.setdefault("JIRA_USER_EMAIL", "test@example.com")
os.environ.setdefault("JIRA_API_TOKEN", "test-token")
os.environ.setdefault("CONFLUENCE_BASE_URL", "https://mock-confluence.example.com")
os.environ.setdefault("CONFLUENCE_SPACE_KEY", "TEST")
os.environ.setdefault("STRIPE_API_KEY", "sk_test_fake_key")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_fake_secret")

# Patch PostgreSQL-specific types (ARRAY, JSONB, UUID) to SQLite-compatible equivalents
# MUST happen before any model imports
from sqlalchemy import Text, JSON
from sqlalchemy.dialects import postgresql as _pg

# ARRAY → JSON (stored as JSON array)
_pg.ARRAY = JSON
# JSONB → JSON
_pg.JSONB = JSON
# UUID → Text (SQLite stores UUIDs as text)
import sqlalchemy as _sa
_orig_uuid = _pg.UUID

import uuid as _uuid_mod

class _SQLiteUUID(Text):
    """UUID rendered as TEXT for SQLite compatibility."""
    def __init__(self, as_uuid=False, **kw):
        super().__init__(**kw)
        self.as_uuid = as_uuid

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, _uuid_mod.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if self.as_uuid:
            return _uuid_mod.UUID(value)
        return value

_pg.UUID = _SQLiteUUID

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event as _sa_event


import re as _re
_HEX_ONLY = _re.compile(r'^[0-9a-f]{32}$')


def _normalize_uuid(val):
    """Ensure UUIDs are stored with hyphens (canonical form) in SQLite."""
    import uuid as _u
    if isinstance(val, _u.UUID):
        return str(val)  # 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    if isinstance(val, str) and _HEX_ONLY.match(val):
        # postgresql.UUID.process_bind_param emits .hex (no dashes) — re-add dashes
        try:
            return str(_u.UUID(val))
        except ValueError:
            return val
    return val


def _patch_sqlite_params(cursor, statement, parameters, context, executemany):
    """Normalize UUID values to hyphenated string form before SQLite sees them."""
    if isinstance(parameters, (list, tuple)):
        parameters = tuple(_normalize_uuid(p) for p in parameters)
    elif isinstance(parameters, dict):
        parameters = {k: _normalize_uuid(v) for k, v in parameters.items()}
    return statement, parameters


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def app():
    """Build FastAPI app against in-memory SQLite (no Postgres required)."""
    from sqlalchemy.ext.asyncio import create_async_engine as _cae
    import app.core.database as _db

    sqlite_engine = _cae(TEST_DB_URL, echo=False)

    # Hook to convert UUID objects → str before SQLite executes
    from sqlalchemy import event as _sae
    from sqlalchemy.engine import Engine as _Eng

    @_sae.listens_for(sqlite_engine.sync_engine, "before_cursor_execute", retval=True)
    def _uuid_fix(conn, cursor, statement, parameters, context, executemany):
        return _patch_sqlite_params(cursor, statement, parameters, context, executemany)

    _db.engine = sqlite_engine
    _db.async_session = async_sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)

    from app.main import app as fastapi_app
    from app.core.database import Base

    async with sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield fastapi_app

    async with sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await sqlite_engine.dispose()


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def auth_client(client):
    """Client with valid JWT token from registered test user."""
    # Register (ignore 409 if already exists)
    await client.post("/api/v1/auth/register", json={
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "full_name": "Test User",
    })
    # Login
    resp = await client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "TestPass123!",
    })
    token = resp.json().get("access_token", "")
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
    client.headers.pop("Authorization", None)
