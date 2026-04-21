# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Upcoming: advanced user management, enhanced dashboard

---

## [0.11.0] - 2026-04-21 — Phase 4: True Integration Tests

- Changed: replaced mocked Strava integration tests with real end-to-end tests against an ephemeral PostgreSQL DB
- Changed: merged `alembic upgrade head` into `test-runner` (removed separate `migrate-test` container) to fix Docker DNS instability
- Changed: per-test isolation via SAVEPOINT rollback; only outbound Strava HTTP calls are mocked

---

## [0.10.0] - 2026-04-20 — Phase 3: Token Management & API

- Added: `StravaActivity`, `StravaActivitiesResponse`, `StravaStatus` Pydantic schemas
- Added: `get_valid_token()` — decrypts token, auto-refreshes within 5-minute safety window, raises `TokenRevokedError` on failure
- Changed: `/api/strava/activities` and `/api/strava/user` now authenticate via `get_current_user` + `get_valid_token()` instead of raw `Authorization` header
- Fixed: `revoke_and_delete()` crash when user has no token record
- Removed: dead `_extract_bearer_token` helper and `get_user_bearer_token` alias

---

## [0.9.0] - 2026-04-05 — Docker Compose Restructure

- Changed: split monolithic `docker-compose-dev.yml` into `docker-compose.yml` (base), `.dev.yml`, and `.prod.yml`
- Added: `migrate` init container; backend now waits for migrations to complete before starting
- Removed: dead `UserInDB` and `UserResponse` Pydantic schemas
- Changed: `app/database.py` now fails fast with a clear error if `DATABASE_URL` is unset
- Fixed: frontend Docker build failure due to `eslint-plugin-react-hooks@5.x` / ESLint 10 peer dep conflict

---

## [0.8.0] - 2026-04-05 — Phase 1: Database Foundation

- Added: SQLAlchemy 2.0 async engine, `get_db` dependency, `UserORM` model, `UserRepository`, Alembic migrations
- Changed: Pydantic schemas moved from `app/models/` → `app/schemas/`; ORM models now exclusively in `app/models/`
- Changed: auth service wired to real DB session; `fake_users_db` removed

---

## [0.7.0] - 2026-04-05 — Phase 0: Dependency & Runtime Upgrades

- Changed: Python 3.13 → 3.14, PostgreSQL 17 → 18
- Changed: `passlib`+`bcrypt<4` → `pwdlib[bcrypt]`; `python-jose` (CVEs) → `PyJWT>=2.8.0`
- Changed: frontend — `react-router@7`, Vite 8, TypeScript 6, React 19
- Fixed: deprecated `datetime.utcnow()` replaced with `datetime.now(timezone.utc)` throughout
- Note: PG17 data volumes must be wiped before starting PG18

---

## [0.6.0] - 2025-11-29 — Strava OAuth Integration

- Added: Strava OAuth 2.0 Authorization Code flow (`/api/strava/connect`, `/api/strava/callback`)
- Added: `httpx` for async HTTP to Strava API; `email-validator` dependency

---

## [0.5.0] - 2025-11-23 — Settings UI & CSS Modules

- Added: Settings page (profile, security, preferences, notifications, third-party connections)
- Added: `ConnectionCard` component for external service integrations
- Added: configurable `Layout` with `Header`, `Footer`, `Sidebar` subcomponents
- Changed: full CSS Modules migration across all frontend components

---

## [0.4.0] - 2025-09-20 — Docker & Infrastructure

- Added: multi-stage Docker builds, Traefik reverse proxy (`cycloveda.local` / `api.cycloveda.local`)
- Added: `GET /health` endpoint, non-root container users, CSP in Nginx
- Changed: CORS handling centralised at Traefik; FastAPI CORS middleware removed

---

## [0.3.0] - 2025-08-18 — Docs & Login Polish

- Added: ADR system, JWT ADR, API reference, architecture and auth guides
- Changed: login page UI improvements

---

## [0.2.0] - 2025-07-26 — Initial Full-Stack App

- Added: React + TypeScript frontend with JWT auth, protected routes, error boundaries
- Added: FastAPI backend with clean architecture, case-sensitive email auth, password hashing
- Added: `pytest` test suite (unit + integration)

---

## [0.1.0] - 2025-07-19 — Project Bootstrap

- Added: initial FastAPI and React scaffolding, git init, basic project config

[Unreleased]: https://github.com/rhish9h/cyclo-veda/compare/v0.11.0...HEAD
[0.11.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rhish9h/cyclo-veda/releases/tag/v0.1.0
