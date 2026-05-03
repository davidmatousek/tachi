"""Application middleware configuration.

Register all middleware in register_middleware(). FastAPI processes
middleware in reverse registration order (last registered runs first).
"""

import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def register_middleware(app: FastAPI) -> None:
    """Register all application middleware.

    CORS must be registered for the React frontend to communicate
    with the API. Never use allow_origins=["*"] with
    allow_credentials=True.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def request_timing(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        """Add X-Process-Time header to every response."""
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}ms"
        return response
