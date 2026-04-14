"""Execution Console FastAPI app — PRJ0-56."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .services.event_store import init_db

app = FastAPI(title="Claude Execution Console", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    init_db()
