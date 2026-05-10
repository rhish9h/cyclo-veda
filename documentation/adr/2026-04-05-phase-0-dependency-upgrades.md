# Phase 0: Dependency & Runtime Upgrades

**Date:** 2026-04-05

## Status

Accepted

## Context

Before adding the database layer (Phase 1), all major runtime and library versions were brought up to date. Multiple components were significantly out of date, and two production backend libraries were abandoned with known issues:

- `passlib` has not been maintained since 2020. The project was pinning `bcrypt<4.0.0` specifically to work around a breakage passlib introduced with newer bcrypt versions.
- `python-jose` last released in 2023, has open CVEs, and FastAPI's own documentation now recommends replacing it with `PyJWT`.
- PostgreSQL 17.7 → 18.3 is a major version bump that also changed the expected volume mount path (`/var/lib/postgresql/data` → `/var/lib/postgresql`).
- Frontend was on Vite 7, TypeScript 5, ESLint 9, and using `react-router-dom` (the legacy shim) instead of `react-router` directly.

## Decision

### Backend
- Replace `passlib` + pinned `bcrypt<4.0.0` with `pwdlib[bcrypt]>=0.2.0` (actively maintained passlib successor).
- Replace `python-jose[cryptography]` with `PyJWT>=2.8.0`. JWT token structure (`sub`, `exp`) unchanged — only signing/decoding library swapped.
- Upgrade Python Docker image: `python:3.13-slim` → `python:3.14-slim`.
- Bump `requires-python` to `>=3.14` in `pyproject.toml`.
- Fix `datetime.utcnow()` (deprecated) in `UserInDB` to `datetime.now(timezone.utc)`.
- Upgrade PostgreSQL: `17.7` → `18.3`. Update volume mount to `/var/lib/postgresql` per PG18 requirements.

### Frontend
- Replace `react-router-dom@^7.7.0` + `@types/react-router-dom@^5.3.3` with `react-router@^7.14.0`. The v7 DOM shim is legacy; all exports are now in the core package.
- Upgrade Vite `7` → `8.0.3`, `@vitejs/plugin-react` `4` → `6.0.1`.
- Upgrade TypeScript `~5.8.3` → `^6.0.2`, ESLint `9` → `10.2.0`.
- Bump minor packages: `react`/`react-dom` → `19.2.4`, `prettier` → `3.8.1`, `typescript-eslint` → `8.58.0`.
- Add `.nvmrc` (pins Node 24) and `engines` field to `package.json`.
- Fix `eslint.config.js`: removed non-existent `@typescript-eslint/prefer-const` rule, dropped `recommendedTypeChecked` preset (requires full type-aware linting not yet applicable to this codebase), added `caughtErrorsIgnorePattern` to allow `_error` in catch blocks.

## Consequences

### Breaking Changes
- **bcrypt 72-byte password limit now enforced**: `pwdlib` raises `ValueError` for passwords longer than 72 bytes. Previously `passlib` silently truncated. The test for 1000-char passwords was updated to test the 72-byte boundary instead. The application does not currently accept passwords longer than 72 bytes at registration (no registration endpoint yet), so no user impact.
- **PostgreSQL volume path changed**: Old `postgres-data` volumes mounted at `/var/lib/postgresql/data` are incompatible with PG18. The volume was wiped (dev environment only — no persistent user data existed). Production deployments will require a `pg_upgrade` path.
- **`react-router-dom` removed**: All 7 source files updated to import from `react-router` directly. API is identical; only the package name changed.

### No Breaking Changes
- JWT token structure (`sub`, `exp`, `HS256`) is identical — existing tokens remain valid.
- All auth API contracts (`/api/auth/login`, `/api/auth/me`) unchanged.
- Backend test suite: 76 passed, 0 failures after upgrades.
- Frontend `check-all` (type-check + lint + format): passes with 0 errors.

## Alternatives Considered

- **Stay on passlib**: Not viable — incompatible with Python 3.14 and requires bcrypt pin that prevents security updates.
- **Stay on python-jose**: Not viable — open CVEs, abandoned, incompatible with Python 3.14 path.
- **Defer PostgreSQL upgrade**: Could have stayed on PG17 to avoid the volume migration complexity, but PG17 reaches end-of-life in November 2027 and upgrading before adding the database schema (Phase 1) is cheaper than migrating a populated database later.
- **Stay on ESLint 9**: Valid option, but ESLint 10 drops deprecated APIs used in older configs. Upgrading now keeps the toolchain current.

## Notes

- `eslint-plugin-react-hooks@5.2.0` declares peer dep support up to ESLint 9 only (not updated yet). The plugin works correctly with ESLint 10 at runtime — the peer dep warning is a stale declaration. Installed with `--legacy-peer-deps`.
- `@eslint/js` latest available is `10.0.1` (not `10.2.0` as the spec stated). `package.json` uses `^10.0.1`.
