"""Shared test fixtures for async FastAPI testing with in-memory SQLite.

Three-tier fixture pattern:
  1. Engine -- create_async_engine with in-memory SQLite + StaticPool
  2. Session -- async_sessionmaker with transaction rollback (no data persists)
  3. Client -- httpx AsyncClient with ASGITransport (full request pipeline)

ALWAYS use StaticPool for in-memory SQLite test engines -- it shares
one connection across all async tasks (required for in-memory DBs).
ALWAYS clear app.dependency_overrides after each test.
"""

from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Create a session-scoped test engine with in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncIterator[AsyncSession]:
    """Yield a session that rolls back after each test."""
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Provide an async HTTP client wired to the test database session."""

    async def _override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
