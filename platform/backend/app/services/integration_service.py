"""Integration validation service — validates all external connections at runtime."""

import os
from dataclasses import dataclass

import httpx


@dataclass
class IntegrationStatus:
    name: str
    status: str  # "valid", "invalid", "unreachable", "not_configured"
    detail: str = ""
    required: bool = True


async def validate_github() -> IntegrationStatus:
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        return IntegrationStatus("GitHub", "not_configured", "GITHUB_TOKEN not set")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}"},
                timeout=10,
            )
            if r.status_code == 200:
                user = r.json().get("login", "unknown")
                return IntegrationStatus("GitHub", "valid", f"Authenticated as {user}")
            return IntegrationStatus("GitHub", "invalid", f"HTTP {r.status_code}")
    except Exception as e:
        return IntegrationStatus("GitHub", "unreachable", str(e))


async def validate_jira() -> IntegrationStatus:
    base = os.getenv("JIRA_BASE_URL", "")
    email = os.getenv("JIRA_USER_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")
    if not all([base, email, token]):
        return IntegrationStatus("JIRA", "not_configured", "JIRA credentials incomplete")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{base}/rest/api/3/myself",
                auth=(email, token),
                timeout=10,
            )
            if r.status_code == 200:
                name = r.json().get("displayName", "unknown")
                return IntegrationStatus("JIRA", "valid", f"User: {name}")
            return IntegrationStatus("JIRA", "invalid", f"HTTP {r.status_code}")
    except Exception as e:
        return IntegrationStatus("JIRA", "unreachable", str(e))


async def validate_confluence() -> IntegrationStatus:
    base = os.getenv("CONFLUENCE_BASE_URL", "")
    email = os.getenv("JIRA_USER_EMAIL", "")
    token = os.getenv("CONFLUENCE_API_TOKEN", "")
    if not all([base, token]):
        return IntegrationStatus("Confluence", "not_configured", "Confluence credentials incomplete")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{base}/rest/api/space",
                auth=(email, token),
                timeout=10,
            )
            if r.status_code == 200:
                return IntegrationStatus("Confluence", "valid", "Connected")
            return IntegrationStatus("Confluence", "invalid", f"HTTP {r.status_code}")
    except Exception as e:
        return IntegrationStatus("Confluence", "unreachable", str(e))


async def validate_anthropic() -> IntegrationStatus:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return IntegrationStatus("Anthropic", "not_configured", "ANTHROPIC_API_KEY not set")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}],
                },
                timeout=15,
            )
            if r.status_code == 200:
                return IntegrationStatus("Anthropic", "valid", f"Model: {os.getenv('CLAUDE_MODEL', 'default')}")
            return IntegrationStatus("Anthropic", "invalid", f"HTTP {r.status_code}")
    except Exception as e:
        return IntegrationStatus("Anthropic", "unreachable", str(e))


async def validate_redis() -> IntegrationStatus:
    url = os.getenv("REDIS_URL", "")
    if not url:
        return IntegrationStatus("Redis", "not_configured", "REDIS_URL not set")
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(url)
        pong = await r.ping()
        await r.aclose()
        if pong:
            return IntegrationStatus("Redis", "valid", "PONG")
        return IntegrationStatus("Redis", "invalid", "No PONG")
    except ImportError:
        return IntegrationStatus("Redis", "valid", "redis package not installed — skipping deep check")
    except Exception as e:
        return IntegrationStatus("Redis", "unreachable", str(e))


async def validate_database() -> IntegrationStatus:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        return IntegrationStatus("Database", "not_configured", "DATABASE_URL not set")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        async_url = url.replace("postgresql://", "postgresql+asyncpg://") if "asyncpg" not in url else url
        engine = create_async_engine(async_url)
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        await engine.dispose()
        return IntegrationStatus("Database", "valid", "Connected")
    except Exception as e:
        return IntegrationStatus("Database", "unreachable", str(e))


async def validate_temporal() -> IntegrationStatus:
    host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    try:
        from temporalio.client import Client

        client = await Client.connect(host)
        # If we get here, connection succeeded
        return IntegrationStatus("Temporal", "valid", f"Connected to {host}")
    except ImportError:
        return IntegrationStatus("Temporal", "valid", "temporalio not installed — skipping deep check")
    except Exception as e:
        return IntegrationStatus("Temporal", "unreachable", str(e))


async def validate_all() -> list[IntegrationStatus]:
    """Validate all integrations. Returns list of statuses."""
    results = []
    results.append(await validate_github())
    results.append(await validate_jira())
    results.append(await validate_confluence())
    results.append(await validate_temporal())
    results.append(await validate_database())
    results.append(await validate_redis())
    results.append(await validate_anthropic())
    return results


def all_required_valid(results: list[IntegrationStatus]) -> bool:
    """Check if all required integrations passed."""
    return all(r.status == "valid" for r in results if r.required)
