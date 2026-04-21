"""Integration test fixtures for tests that require a live database.

These fixtures connect to the DATABASE_URL from the environment (set via
.env.test in CI / docker-compose.test.yml) and wrap each test in a
nested transaction (SAVEPOINT) that is rolled back after the test, keeping
the DB clean between tests without truncating tables.

The get_db dependency override here takes precedence over the autouse mock
in the root conftest.py because FastAPI uses the last-registered override.
"""

import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
import os

from app.main import app
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.schemas.user import User


@pytest.fixture(scope="session")
def real_engine():
    """Create a single async engine for the entire integration test session.

    Uses NullPool so each connection is created fresh — required for the
    nested-transaction rollback pattern with asyncpg.
    """
    from sqlalchemy.pool import NullPool

    url = os.environ["DATABASE_URL"]
    engine = create_async_engine(url, poolclass=NullPool)
    return engine


@pytest_asyncio.fixture
async def real_db(real_engine):
    """Yield a real AsyncSession wrapped in a rolled-back transaction.

    Pattern:
        1. Open a connection and BEGIN an outer transaction.
        2. Create a SAVEPOINT (nested transaction).
        3. Bind the session to that connection.
        4. After the test, roll back to the SAVEPOINT → DB is pristine.

    This means every test starts with the post-migration schema but zero
    application data, and writes are never committed to the DB.
    """
    async with real_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()  # SAVEPOINT

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
