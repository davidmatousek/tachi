"""SQLAlchemy DeclarativeBase with timestamp mixin.

All ORM models should inherit from Base. The TimestampMixin provides
created_at and updated_at columns automatically.

Example:
    from app.db.base import Base, TimestampMixin

    class User(TimestampMixin, Base):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(unique=True, index=True)
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns.

    Include before Base in the class hierarchy:
        class MyModel(TimestampMixin, Base): ...
    """

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
