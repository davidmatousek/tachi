"""Async database engine and session factory.

Uses SQLAlchemy 2.0 async API with asyncpg driver.
expire_on_commit=False is CRITICAL -- without it, accessing model
attributes after commit raises MissingGreenlet errors in async contexts.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
