"""Shared FastAPI dependencies.

All request-scoped resources (database sessions, auth) are provided
as Depends() callables. Routes inject these -- never import db or
auth utilities directly.
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield an async database session for the request lifecycle.

    The session is automatically closed when the request completes.
    """
    async with async_session_factory() as session:
        yield session


async def get_current_user() -> None:
    """Placeholder for authenticated user dependency.

    Replace this stub with JWT token validation and user lookup
    once the auth service is implemented.
    """
    raise NotImplementedError(
        "Authentication not yet implemented. "
        "Replace this stub in app/api/deps.py."
    )
