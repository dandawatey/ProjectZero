from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base
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
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="ProjectZero Factory API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/health")
async def health():
    return {"status": "ok"}
