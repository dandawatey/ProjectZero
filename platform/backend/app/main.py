import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.core.config import get_settings
from app.core.middleware import JWTAuthMiddleware
import app.models.metrics  # noqa: F401 — registers CxoMetricsCache with Base
import app.models.user     # noqa: F401 — registers User + RefreshToken with Base
import app.models.product  # noqa: F401 — registers Product with Base
from app.api.routes import (
    workflows,
    steps,
    approvals,
    agents,
    artifacts,
    audit,
    dashboard,
    triggers,
    integrations,
    activities,
    temporal_status,
    brain,
    dev_monitor,
    cxo_metrics,
    confluence,
    auth,
    products,
    commands,
)
from app.services.integration_health import validate_on_startup, start_all_monitors
from app.temporal_integration.worker import start_worker, stop_worker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # One-shot startup validation for JIRA + Confluence
    settings = get_settings()
    startup_results = await validate_on_startup()
    logger.info("Integration startup check: %s", startup_results)

    # Start background health monitors (non-blocking)
    await start_all_monitors(settings)

    # Start Temporal worker (non-blocking — skips gracefully if Temporal not running)
    await start_worker()

    yield

    await stop_worker()
    await engine.dispose()


app = FastAPI(
    title="ProjectZero Factory API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS must be outermost (added last = runs first in Starlette LIFO order)
# JWTAuthMiddleware added first = runs after CORS so OPTIONS preflight passes through
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(steps.router, prefix="/api/v1/steps", tags=["steps"])
app.include_router(approvals.router, prefix="/api/v1/approvals", tags=["approvals"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(artifacts.router, prefix="/api/v1/artifacts", tags=["artifacts"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(triggers.router, prefix="/api/v1/triggers", tags=["triggers"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(activities.router, prefix="/api/v1/activities", tags=["activities"])
app.include_router(temporal_status.router, prefix="/api/v1/temporal", tags=["temporal"])
app.include_router(brain.router, prefix="/api/v1/brain", tags=["brain"])
app.include_router(dev_monitor.router, prefix="/api/v1/dev", tags=["dev-monitor"])
app.include_router(cxo_metrics.router, prefix="/api/v1/cxo", tags=["cxo"])
app.include_router(confluence.router, prefix="/api/v1/confluence", tags=["confluence"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(commands.router, prefix="/api/v1/commands", tags=["commands"])


@app.get("/health")
async def health():
    return {"status": "ok"}
