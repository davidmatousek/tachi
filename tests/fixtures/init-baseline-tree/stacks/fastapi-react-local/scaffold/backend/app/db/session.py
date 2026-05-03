"""Async database engine and session factory.

Uses SQLAlchemy 2.0 async API with aiosqlite driver.
expire_on_commit=False is CRITICAL -- without it, accessing model
attributes after commit raises MissingGreenlet errors in async contexts.

SQLite-specific setup:
  - WAL mode for concurrent read performance
  - Foreign keys enabled per connection (OFF by default in SQLite)
  - Busy timeout to handle write contention
"""

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, connection_record):
    """Configure SQLite pragmas on every new connection.

    - journal_mode=WAL: allows concurrent reads during writes
    - busy_timeout=5000: wait up to 5s instead of failing on lock
    - foreign_keys=ON: enforce FK constraints (OFF by default in SQLite)
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
