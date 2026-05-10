"""SQLAlchemy ORM model for stored Strava OAuth tokens.

Maps to the strava_tokens table (one to one with users).
Token secrets are stored encrypted via utils/security.py.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class StravaTokenORM(Base):
    """Stores encrypted Strava OAuth tokens for a single user.

    Unique constraint ensures exactly one token record per user.
    """

    __tablename__ = "strava_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    strava_athlete_id: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True, index=True)

    # Encrypted token fields (stored as Base64 strings)
    access_token: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    token_type: Mapped[str | None] = mapped_column(String(50), nullable=True, default="Bearer")
    expires_in: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    # Optional metadata
    scope: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_strava_tokens_user_id"),
        UniqueConstraint("strava_athlete_id", name="uq_strava_tokens_athlete_id"),
        ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name="fk_strava_tokens_user_id",
        ),
    )
