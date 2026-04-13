"""Integration health monitor with circuit breaker pattern.

Runs background keep-alive loops for JIRA and Confluence.
Exposes a shared health registry consumed by the /integrations/health endpoint.

Circuit breaker states:
  CLOSED   — service healthy, requests flow through
  OPEN     — failure threshold exceeded, requests blocked, retry after timeout
  HALF_OPEN — one trial request allowed to test recovery
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Awaitable

import httpx

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------

class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 3
    recovery_timeout: int = 30  # seconds

    _failures: int = field(default=0, init=False)
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _opened_at: float | None = field(default=None, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if self._opened_at and (time.monotonic() - self._opened_at) >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                logger.info("[%s] Circuit → HALF_OPEN (testing recovery)", self.name)
        return self._state

    def record_success(self) -> None:
        if self._state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            logger.info("[%s] Circuit → CLOSED (recovered)", self.name)
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._state == CircuitState.HALF_OPEN:
            # Trial failed — reopen
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()
            logger.warning("[%s] Circuit → OPEN (half-open trial failed)", self.name)
        elif self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()
            logger.warning(
                "[%s] Circuit → OPEN after %d failures", self.name, self._failures
            )

    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    def allow_request(self) -> bool:
        s = self.state
        return s in (CircuitState.CLOSED, CircuitState.HALF_OPEN)


# ---------------------------------------------------------------------------
# Health registry (singleton)
# ---------------------------------------------------------------------------

@dataclass
class ServiceHealth:
    name: str
    status: str = "unknown"       # healthy | degraded | unreachable | not_configured
    last_checked: float = 0.0
    last_error: str = ""
    circuit: CircuitBreaker = field(default_factory=lambda: CircuitBreaker("default"))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "circuit_state": self.circuit.state.value,
            "last_checked": self.last_checked,
            "last_error": self.last_error,
        }


class IntegrationHealthRegistry:
    """Shared registry for all integration health states."""

    def __init__(self) -> None:
        self._services: dict[str, ServiceHealth] = {}

    def register(self, name: str, failure_threshold: int = 3, recovery_timeout: int = 30) -> ServiceHealth:
        if name not in self._services:
            self._services[name] = ServiceHealth(
                name=name,
                circuit=CircuitBreaker(name, failure_threshold, recovery_timeout),
            )
        return self._services[name]

    def get(self, name: str) -> ServiceHealth | None:
        return self._services.get(name)

    def all(self) -> list[dict]:
        return [s.to_dict() for s in self._services.values()]

    def all_healthy(self) -> bool:
        return all(s.status == "healthy" for s in self._services.values())


# Global registry
health_registry = IntegrationHealthRegistry()


# ---------------------------------------------------------------------------
# Probe functions
# ---------------------------------------------------------------------------

async def _probe_jira() -> tuple[bool, str]:
    base = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    email = os.getenv("JIRA_USER_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")
    if not all([base, email, token]):
        return False, "not_configured"
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{base}/rest/api/3/myself", auth=(email, token), timeout=10)
            if r.status_code == 200:
                return True, r.json().get("displayName", "ok")
            return False, f"HTTP {r.status_code}"
    except Exception as exc:
        return False, str(exc)


async def _probe_confluence() -> tuple[bool, str]:
    base = os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")
    email = os.getenv("JIRA_USER_EMAIL", "")
    token = os.getenv("CONFLUENCE_API_TOKEN", "") or os.getenv("JIRA_API_TOKEN", "")
    if not all([base, email, token]):
        return False, "not_configured"
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{base}/rest/api/space", params={"limit": 1}, auth=(email, token), timeout=10)
            if r.status_code == 200:
                return True, "ok"
            return False, f"HTTP {r.status_code}"
    except Exception as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Background monitor loops
# ---------------------------------------------------------------------------

async def _monitor_loop(
    service_name: str,
    probe: Callable[[], Awaitable[tuple[bool, str]]],
    interval: int,
    failure_threshold: int,
    recovery_timeout: int,
) -> None:
    svc = health_registry.register(service_name, failure_threshold, recovery_timeout)
    logger.info("[%s] Health monitor started (interval=%ds)", service_name, interval)

    while True:
        if svc.circuit.allow_request():
            ok, detail = await probe()
            svc.last_checked = time.monotonic()
            if ok:
                svc.circuit.record_success()
                svc.status = "healthy"
                svc.last_error = ""
            else:
                if detail == "not_configured":
                    svc.status = "not_configured"
                    svc.last_error = detail
                    # No point hammering an unconfigured service
                    await asyncio.sleep(interval * 10)
                    continue
                svc.circuit.record_failure()
                svc.status = "unreachable" if svc.circuit.is_open() else "degraded"
                svc.last_error = detail
                logger.warning("[%s] Probe failed: %s (circuit=%s)", service_name, detail, svc.circuit.state.value)
        else:
            logger.debug("[%s] Circuit OPEN — skipping probe", service_name)

        await asyncio.sleep(interval)


async def start_jira_monitor(interval: int = 60, failure_threshold: int = 3, recovery_timeout: int = 30) -> None:
    asyncio.create_task(
        _monitor_loop("JIRA", _probe_jira, interval, failure_threshold, recovery_timeout),
        name="jira-health-monitor",
    )


async def start_confluence_monitor(interval: int = 60, failure_threshold: int = 3, recovery_timeout: int = 30) -> None:
    asyncio.create_task(
        _monitor_loop("Confluence", _probe_confluence, interval, failure_threshold, recovery_timeout),
        name="confluence-health-monitor",
    )


async def start_all_monitors(settings=None) -> None:
    """Start JIRA + Confluence health monitors using settings or env defaults."""
    if settings:
        ji = settings.jira_health_interval
        jt = settings.jira_circuit_breaker_threshold
        jr = settings.jira_circuit_breaker_timeout
        ci = settings.confluence_health_interval
    else:
        ji, jt, jr, ci = 60, 3, 30, 60

    await start_jira_monitor(ji, jt, jr)
    await start_confluence_monitor(ci, jt, jr)
    logger.info("All integration health monitors started")


# ---------------------------------------------------------------------------
# Startup validation (one-shot, blocking)
# ---------------------------------------------------------------------------

async def validate_on_startup() -> dict[str, str]:
    """
    Run one-shot JIRA + Confluence probes at startup.
    Returns {"jira": "healthy|...", "confluence": "healthy|..."}.
    Logs warnings but does NOT block startup on failure.
    """
    results: dict[str, str] = {}

    ok, detail = await _probe_jira()
    jira_svc = health_registry.register("JIRA")
    if ok:
        jira_svc.status = "healthy"
        jira_svc.circuit.record_success()
        logger.info("[JIRA] Startup check passed: %s", detail)
        results["jira"] = "healthy"
    else:
        jira_svc.status = "not_configured" if detail == "not_configured" else "unreachable"
        jira_svc.last_error = detail
        logger.warning("[JIRA] Startup check failed: %s", detail)
        results["jira"] = jira_svc.status

    ok, detail = await _probe_confluence()
    conf_svc = health_registry.register("Confluence")
    if ok:
        conf_svc.status = "healthy"
        conf_svc.circuit.record_success()
        logger.info("[Confluence] Startup check passed")
        results["confluence"] = "healthy"
    else:
        conf_svc.status = "not_configured" if detail == "not_configured" else "unreachable"
        conf_svc.last_error = detail
        logger.warning("[Confluence] Startup check failed: %s", detail)
        results["confluence"] = conf_svc.status

    return results
