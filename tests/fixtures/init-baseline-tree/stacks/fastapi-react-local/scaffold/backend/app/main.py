"""FastAPI application factory with lifespan management."""

import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import settings
from app.core.middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle.

    Startup: ensures the SQLite data directory exists.
    Add additional startup logic (caches, background tasks) before yield.
    Add shutdown/cleanup logic after yield.
    """
    # Ensure SQLite data directory exists
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        db_path = db_url.split("///")[-1]
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    yield
    # Shutdown: release resources here


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="App",
        version="0.1.0",
        lifespan=lifespan,
    )

    register_middleware(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Root health check endpoint."""
        return {"status": "ok"}

    return app


app = create_app()
