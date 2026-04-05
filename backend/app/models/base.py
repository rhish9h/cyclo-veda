"""SQLAlchemy declarative base with shared timestamp columns.

All ORM models should inherit from Base. The created_at and updated_at
columns are timezone-aware (TIMESTAMP WITH TIME ZONE) and auto-populated.

Naming convention:
- models/   → SQLAlchemy ORM models (this package)
- schemas/  → Pydantic models for API validation (app/schemas/)
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, MappedColumn


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""

    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
