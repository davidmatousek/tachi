"""Alembic async migration environment.

Loads DATABASE_URL from environment (not hardcoded in alembic.ini).
Uses run_sync() to bridge Alembic's synchronous API with the async engine.

Import all ORM models here so autogenerate can detect schema changes.
"""

import asyncio
import os

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Import Base so Alembic can read model metadata for autogenerate.
# Import all model modules here to register them with Base.metadata.
from app.db.base import Base

# Add model imports below as you create them:
# from app.models import user  # noqa: F401

target_metadata = Base.metadata


def get_database_url() -> str:
    """Read DATABASE_URL from environment, falling back to alembic.ini."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    return context.config.get_main_option("sqlalchemy.url", "")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script generation)."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:  # type: ignore[no-untyped-def]
    """Execute migrations within a synchronous connection context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with an async engine.

    Uses run_sync() to bridge the synchronous Alembic API with
    the async SQLAlchemy engine.
    """
    engine = create_async_engine(get_database_url())

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
