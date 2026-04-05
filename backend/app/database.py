"""Database connection and session management.

Uses sync SQLAlchemy (simpler, matches current FastAPI patterns).
All sync DB calls from async route handlers must be wrapped in
asyncio.to_thread() to avoid blocking the event loop.

Session usage:
    from app.database import get_db
    from sqlalchemy.orm import Session

    def my_endpoint(db: Session = Depends(get_db)):
        ...
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Copy backend/.env.example to backend/.env and fill in your credentials."
        )
    return url


def _make_engine():
    return create_engine(
        _get_database_url(),
        pool_pre_ping=True,  # Verify connections before use (handles stale connections)
        pool_size=5,
        max_overflow=10,
        connect_args={},
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
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _SessionLocal


def get_db():
    """FastAPI dependency that yields a database session.

    Ensures the session is always closed after the request, even on errors.
    The engine and session factory are created on first call (lazy init).

    Yields:
        Session: SQLAlchemy database session
    """
    db: Session = _session_factory()()
    try:
        yield db
    finally:
        db.close()
