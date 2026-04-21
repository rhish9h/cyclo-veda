# Integration Test Strategy: Real DB + HTTP Mocks Only

**Date:** 2026-04-21
**Status:** Accepted

## Context

Phase 3 delivered Strava OAuth endpoints (connect, callback, status, disconnect, activities). The original integration tests for these endpoints mocked the DB session, repositories, and services — making them effectively glorified unit tests that gave no confidence in the actual data flow through the stack.

A real PostgreSQL container was already available via `docker-compose.test.yml`, but it was only used by a separate `migrate-test` service. The test-runner itself was still using mocks.

## Decision

Replace all mocked integration tests with **true integration tests**:

1. **Real PostgreSQL** — tests talk to the same ephemeral DB that migrations are applied to.
2. **Mock only outbound HTTP** — `httpx.AsyncClient` calls to `api.strava.com` and `www.strava.com/oauth/token` are patched; nothing else is mocked.
3. **Per-test rollback via SAVEPOINT** — each test runs inside a `BEGIN` → `SAVEPOINT` → `ROLLBACK` cycle so the DB is clean between tests without truncating tables.
4. **Real encryption** — `STRAVA_ENCRYPTION_KEY` from `.env.test` is used; token encrypt/decrypt goes through real Fernet.
5. **FastAPI dependency overrides** — `get_db` is overridden with the test session; `get_current_user` is overridden with a fixed `User(id=1)`.

### Key implementation details

**Single test-runner container**  
Migrations are run as part of the `test-runner` command (`alembic upgrade head && pytest ...`) rather than in a separate `migrate-test` container. When `migrate-test` exited under `docker compose up --exit-code-from`, Docker's network DNS briefly reshuffled, causing `socket.gaierror: [Errno -2] Name or service not known` at conftest import time. Folding migrations into the test-runner eliminates the mid-session container exit.

**Seed user committed at import time**  
`strava_tokens.user_id` is a FK to `users.id`. The savepoint rollback pattern means test writes never reach the real DB — but PostgreSQL enforces FK constraints at the moment of INSERT (not at commit). The seed user must therefore be **fully committed** before the first test runs.

Session-scoped `@pytest_asyncio.fixture` cannot reliably commit because pytest-asyncio's function-scoped event loop tears down between fixtures. The fix: call `asyncio.run(_seed())` directly at conftest module import time — guaranteed to run before any fixture setup.

**`db.expire_all()` after `store_tokens()`**  
`strava_service.store_tokens()` mutates the returned `StravaTokenORM` record's `access_token` field to plaintext (for caller convenience). SQLAlchemy's identity map then serves this in-memory record to the next `get_by_user_id` call within the same session — including calls from the endpoint under test. The endpoint then tries to Fernet-decrypt a plaintext string and raises `TokenRevokedError` → HTTP 401.

Fix: wrap `store_tokens` in a test helper that calls `db.expire_all()` after each write, forcing all subsequent queries to re-read from the DB.

**`DATABASE_URL` captured at import time**  
The root `conftest.py` has a `reset_environment` autouse fixture that clears `os.environ` after every test. Since `real_db` opens a new connection per test during setup, `DATABASE_URL` must be captured before `reset_environment` can wipe it. Capturing it in a module-level variable at integration `conftest.py` import time solves this.

## Consequences

### Positive
- Tests verify the full stack: routing → auth → service → repository → DB → serialisation.
- FK constraints, encryption, and SQL query correctness are all exercised.
- Faults in any layer (e.g., wrong column name, misconfigured session) are caught immediately.
- Test isolation is maintained via SAVEPOINT rollback — no table truncation needed.

### Negative
- Integration tests require Docker; they cannot run locally without Compose.
- Import-time `asyncio.run()` is unusual and slightly fragile — if the conftest is imported in an environment without a reachable DB (e.g., unit-test-only runs), it will fail.
- Per-test overhead is higher than unit tests (~300 ms per test vs ~10 ms).

### Mitigations
- Unit tests are kept separate (`tests/unit/`) and run without Docker (`pytest tests/unit --override-ini="addopts=" -p no:cov`).
- The import-time seed is guarded with an `if existing is None` check to be idempotent.

## Alternatives Considered

| Option | Rejected because |
|---|---|
| Keep mocked integration tests | Give no confidence in DB/SQL correctness; essentially duplicate unit tests |
| Use `pytest-docker` / `testcontainers` | Adds a dependency; the existing `docker-compose.test.yml` already solves the problem |
| Truncate tables between tests | Slower and stateful; SAVEPOINT rollback is faster and deterministic |
| Session-scoped `@pytest_asyncio.fixture` for seeding | Fails silently — pytest-asyncio's function-scoped event loop doesn't reliably run session-scoped async fixtures before function-scoped ones |

## Future Considerations
- Add integration tests for auth endpoints once they exist.
- Consider `testcontainers-python` if the project moves away from Docker Compose for CI.
- The import-time seed could be replaced with a pytest plugin or `conftest.py` `session`-scoped sync fixture if pytest-asyncio adds proper session-loop support.
