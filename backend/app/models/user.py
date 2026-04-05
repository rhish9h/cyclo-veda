"""SQLAlchemy ORM model for the users table.

Naming convention:
- models/   → SQLAlchemy ORM models for database tables (this file)
- schemas/  → Pydantic models for API request/response validation (app/schemas/user.py)
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserORM(Base):
    """ORM representation of the users table.

    Maps to the 'users' table created by the Alembic migration.
    Timestamps (created_at, updated_at) are inherited from Base.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
