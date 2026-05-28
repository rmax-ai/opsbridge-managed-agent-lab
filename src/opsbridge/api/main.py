"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes_approvals import router as approvals_router
from .routes_demo_scenarios import router as scenarios_router
from .routes_memory import router as memory_router
from .routes_sessions import router as sessions_router
from .routes_webhooks import router as webhooks_router
from .state import MockBackendStore


def create_app() -> FastAPI:
    """Create the OpsBridge backend application."""
    app = FastAPI(title="OpsBridge Backend", version="0.1.0")
    app.state.backend = MockBackendStore()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8501"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(sessions_router)
    app.include_router(approvals_router)
    app.include_router(memory_router)
    app.include_router(webhooks_router)
    app.include_router(scenarios_router)
    return app


app = create_app()
