"""Integration test fixtures for tests that require a live database.

These fixtures connect to the DATABASE_URL from the environment (set via
.env.test in CI / docker-compose.test.yml) and wrap each test in a
nested transaction (SAVEPOINT) that is rolled back after the test, keeping
the DB clean between tests without truncating tables.

The get_db dependency override here takes precedence over the autouse mock
in the root conftest.py because FastAPI uses the last-registered override.
"""

import asyncio
import atexit
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker as _async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.main import app
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.schemas.user import User

# Capture DATABASE_URL once at import time.
# The root conftest reset_environment fixture calls os.environ.clear() + restore
# after every test. Because real_db opens a new connection per test during setup,
# DATABASE_URL must be available then — but reset_environment may have already
# wiped it. Capturing it here avoids that race.
_DATABASE_URL: str = os.environ["DATABASE_URL"]

# Build the engine once for the whole session. NullPool is required for the
# nested-transaction rollback pattern (each test gets its own raw connection).
_engine = create_async_engine(_DATABASE_URL, poolclass=NullPool)


def _run_seed():
    """Insert the integration test user into the DB at import time.

    This runs before pytest collects or sets up any fixtures, guaranteeing the
    user row is committed before any strava_tokens FK insert. atexit handles
    cleanup after the test process exits.
    """
    from app.models.user import UserORM
    from app.services.auth_service import AuthService

    _factory = _async_sessionmaker(_engine, expire_on_commit=False)

    async def _seed():
        async with _factory() as s:
            existing = await s.get(UserORM, 1)
            if existing is None:
                s.add(UserORM(
                    id=1,
                    email="integration@cycloveda.com",
                    username="integration_user",
                    hashed_password=AuthService.get_password_hash("testpass"),
                    is_active=True,
                ))
                await s.commit()

    async def _teardown():
        async with _factory() as s:
            user = await s.get(UserORM, 1)
            if user:
                await s.delete(user)
                await s.commit()
        await _engine.dispose()

    asyncio.run(_seed())

    def _safe_teardown():
        # Best-effort cleanup. The DB is ephemeral (spun down by docker-compose),
        # so a failure here doesn't matter — we just want to avoid a scary
        # "cannot schedule new futures after interpreter shutdown" traceback.
        try:
            asyncio.run(_teardown())
        except Exception:
            pass

    atexit.register(_safe_teardown)


_run_seed()


@pytest.fixture(scope="session")
def real_engine():
    """Return the module-level engine (built once, URL captured at import time)."""
    return _engine


@pytest_asyncio.fixture
async def real_db(real_engine):
    """Yield a real AsyncSession wrapped in a rolled-back savepoint.

    Each test gets a fresh SAVEPOINT. All writes the test makes (token rows,
    etc.) are rolled back after the test — the committed seed user remains
    until the session-scoped seed_user fixture tears it down.
    """
    async with real_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()  # SAVEPOINT — all test writes roll back here

        session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")

        yield session

        await session.close()
        await conn.rollback()


@pytest.fixture
def integration_user() -> User:
    """The mock authenticated user injected into all integration API calls."""
    return User(id=1, email="integration@cycloveda.com", username="integration_user", is_active=True)


@pytest_asyncio.fixture
async def async_client(real_db, integration_user):
    """AsyncClient with the real DB session and mocked auth injected.

    - get_db → real rolled-back session (overrides root conftest mock)
    - get_current_user → integration_user (no JWT required)
    """
    app.dependency_overrides[get_db] = lambda: real_db
    app.dependency_overrides[get_current_user] = lambda: integration_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)
