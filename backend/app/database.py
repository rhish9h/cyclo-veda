"""Database connection and session management.

Uses async SQLAlchemy with AsyncEngine and AsyncSession.
All database operations are natively async and can be awaited
directly from async FastAPI route handlers.

Session usage:
    from app.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    async def my_endpoint(db: AsyncSession = Depends(get_db)):
        ...
"""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Copy backend/.env.example to backend/.env and fill in your credentials."
        )
    return url


def _make_engine():
    return create_async_engine(
        _get_database_url(),
        pool_pre_ping=True,  # Verify connections before use (handles stale connections)
        pool_size=5,
        max_overflow=10,
        connect_args={},  # asyncpg handles most settings automatically
    )


# Engine and session factory are created lazily on first call to get_db().
# This avoids a RuntimeError at import time when DATABASE_URL is not set
# (e.g. during tests, where get_db is overridden by the conftest fixture).
_engine = None
_SessionLocal = None


def _session_factory():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = _make_engine()
        _SessionLocal = async_sessionmaker(
            bind=_engine,
            autocommit=False,
            autoflush=False,
            class_=AsyncSession,
        )
    return _SessionLocal


async def get_db():
    """FastAPI dependency that yields an async database session.

    Ensures the session is always closed after the request, even on errors.
    The engine and session factory are created on first call (lazy init).

    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with _session_factory()() as db:
        yield db
