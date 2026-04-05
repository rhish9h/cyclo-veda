# Phase 1: Database Foundation — SQLAlchemy, Alembic, Repository Layer

**Date:** 2026-04-05

## Status

Implemented

## Context

Cyclo Veda previously had no persistent storage. User data lived in `fake_users_db` (an in-memory dict in `auth_service.py`). This was a deliberate short-term scaffold — it needed to be replaced before Strava OAuth tokens could be securely stored per-user (Phase 2).

Phase 1 establishes the full database foundation so all subsequent phases can persist data reliably.

## Decision

### 1. SQLAlchemy 2.x (sync) over async

Chose **sync SQLAlchemy** with `asyncio.to_thread()` call sites rather than `AsyncSession`. Rationale:

- Simpler mental model; easier to test (no async fixtures needed)
- `asyncio.to_thread()` gives the async benefit (non-blocking event loop) without async ORM complexity
- Can migrate to `AsyncSession` later if profiling shows it is necessary

### 2. Alembic for migrations

Alembic is the standard migration tool for SQLAlchemy. `env.py` reads `DATABASE_URL` from the environment so credentials are never in `alembic.ini`. The first migration (`create_users_table`) was written manually since no live DB is available in the development environment; subsequent migrations will use `--autogenerate` against a running Postgres instance.

### 3. Repository pattern

`UserRepository` (in `app/repositories/`) encapsulates all SQL queries. Benefits:

- Services and routers never write raw queries
- Repository methods are easily mocked in tests without a real DB
- Follows the same pattern planned for `StravaTokenRepository` (Phase 2)

### 4. `models/` vs `schemas/` naming

Renamed directories to eliminate ambiguity:

| Directory | Contains | Purpose |
|-----------|----------|---------|
| `app/models/` | SQLAlchemy ORM classes (`UserORM`) | Database table definitions |
| `app/schemas/` | Pydantic models (`User`, `UserInDB`, …) | API request/response validation |

Previously both lived in `app/models/`, causing confusion about which layer a class belonged to.

### 5. `fake_users_db` removed entirely

Rather than keeping the fake DB as a fallback, it was removed completely. Tests now use an `autouse` fixture in `conftest.py` that:
- Overrides the FastAPI `get_db` dependency with a `MagicMock` session
- Patches `UserRepository.get_by_email` to return pre-built mock rows

This means **no live PostgreSQL connection is required to run the test suite**.

## Consequences

- **Good:** Tests run offline; CI does not need a DB service container
- **Good:** Auth endpoints now return a real `id` on the `User` schema, enabling Phase 2 (`current_user.id` for token storage)
- **Good:** Alembic migration history starts cleanly from a known state
- **Watch:** The first `--autogenerate` migration must be run against a live DB (`docker-compose up`) to produce the full diff; currently the migration was written manually and may need adjustment if ORM model columns change before first deployment
- **Watch:** `asyncio.to_thread()` adds a small thread-pool overhead per DB call; acceptable at current scale

## Alternatives Considered

- **async SQLAlchemy (`AsyncSession`)** — rejected for added complexity with no measured benefit at this stage
- **Tortoise ORM / Databases** — rejected; SQLAlchemy is the ecosystem standard and matches the spec
- **Keep `fake_users_db` as fallback** — rejected; keeping two code paths would mask integration bugs
