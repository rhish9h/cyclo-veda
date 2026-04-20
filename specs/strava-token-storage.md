# Strava Token Storage & Database Integration Specification

## Overview

This specification outlines the implementation of persistent storage for Strava OAuth tokens and the establishment of a proper database layer for Cyclo Veda. Currently, the application uses in-memory storage that loses all data on restart, making Strava integration non-functional.

## Current State

### Problems
- **No Database**: Using `fake_users_db` in-memory dictionary
- **Token Loss**: Strava tokens are printed to console then discarded
- **No Persistence**: All data lost on server restart
- **No Token Refresh**: Cannot handle Strava token expiration
- **Mock Auth**: Authentication not production-ready
- **No User ID**: `User` and `UserInDB` Pydantic models have no `id` field — `id: int` only exists on the unused `UserResponse` model. Phase 2 depends on `current_user.id`, so Phase 1 must add this field.
- **JWT sub is email, not ID**: `create_access_token` encodes `{"sub": user.email}` and `verify_token` decodes `email = payload.get("sub")`. Token-linking in the OAuth callback must remain email-based until the DB migration is complete and user rows have stable integer IDs.
- **No `.env.example` files exist**: The spec references updating `backend/.env.example` but neither `backend/.env.example` nor root `.env.example` currently exist in the repository — they must be created.
- **`datetime.utcnow()` in `UserInDB`**: `created_at` and `updated_at` use the deprecated `datetime.utcnow()` (timezone-naive). Phase 1 must update these to `datetime.now(timezone.utc)` for consistency with the timezone-aware DB schema.

### Existing Assets
- ✅ OAuth flow implemented (`/api/strava/connect`, `/api/strava/callback`)
- ✅ Token exchange logic (`exchange_code_for_tokens()`)
- ✅ Clean architecture patterns (models, services, routers)
- ✅ PostgreSQL container already in `docker-compose-dev.yml` with `postgres-data` volume and health checks
- ✅ Comprehensive testing framework

### Breaking Changes Introduced by This Spec
- **`/api/strava/connect` response type change**: Current implementation returns `RedirectResponse(302)` directly to Strava. The spec changes this to `{"auth_url": ...}` JSON, delegating the redirect to the frontend. This is intentional (required for auth dependency injection) but **must be coordinated with a frontend change**.

## Requirements

### Functional Requirements
1. **Persistent Token Storage**: Store Strava tokens per user with expiration tracking
2. **Token Refresh**: Automatically refresh expired Strava tokens
3. **User Integration**: Link Strava tokens to existing user accounts
4. **Database Migrations**: Version-controlled database schema changes
5. **Token Security**: Secure storage of sensitive OAuth tokens

### Non-Functional Requirements
1. **Backwards Compatibility**: Don't break existing authentication flow
2. **Clean Architecture**: Follow existing patterns (models, services, routers)
3. **Test Coverage**: Unit and integration tests for new database layer
4. **Performance**: Minimal overhead on existing API calls
5. **Security**: Proper token encryption and secure handling

## Technical Design

### Database Choice: PostgreSQL (Existing)
**Rationale**: 
- **Already Available**: PostgreSQL container in both docker-compose.yml and docker-compose-dev.yml (upgrading to 18.3 in Phase 0)
- **Production Ready**: Robust, feature-rich database with excellent SQLAlchemy support
- **Docker Integration**: Already configured with proper networking and health checks
- **Volume Persistence**: `postgres-data` volume configured for data persistence
- **Scalable**: Easy path for future scaling and performance optimization

### Schema Design

#### Users Table (Migration from in-memory)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### Strava Tokens Table (One-to-One Relationship)
```sql
CREATE TABLE strava_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,  -- One user can have at most one Strava account
    strava_athlete_id INTEGER UNIQUE NOT NULL,  -- One Strava athlete can belong to at most one user
    access_token_encrypted TEXT NOT NULL,  -- Encrypted at rest
    refresh_token_encrypted TEXT NOT NULL,  -- Encrypted at rest
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    scope VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance and token refresh logic
CREATE INDEX idx_strava_tokens_user_id ON strava_tokens(user_id);
CREATE INDEX idx_strava_tokens_expires_at ON strava_tokens(expires_at);
CREATE UNIQUE INDEX idx_strava_tokens_athlete_id ON strava_tokens(strava_athlete_id);
```

**Business Rules Enforced:**
- **One-to-One Integration**: Each Cyclo Veda user can link exactly one Strava account
- **Unique Athlete Mapping**: Each Strava athlete can belong to exactly one Cyclo Veda user
- **Token Security**: Access and refresh tokens encrypted at rest

### Architecture Changes

#### New Files
```
backend/
├── alembic.ini                # Alembic configuration
├── migrations/                 # Database migration files
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── database.py            # Database connection & session management
│   ├── models/
│   │   ├── base.py             # SQLAlchemy base model
│   │   ├── user.py             # User database model
│   │   └── strava_token.py     # Strava token database model
│   ├── schemas/
│   │   └── strava.py           # Pydantic response models
│   ├── services/
│   │   ├── auth_service.py     # Updated to use database
│   │   └── strava_service.py   # Strava token management & API calls
│   ├── repositories/
│   │   ├── user_repository.py  # User database operations
│   │   └── strava_token_repository.py  # Strava token database operations
│   ├── utils/
│   │   └── security.py         # Token encryption & OAuth state utilities
│   └── routers/
│       └── strava.py           # Enhanced Strava endpoints
```

#### Updated Files
```
backend/
├── pyproject.toml              # Add SQLAlchemy, Alembic, cryptography dependencies
├── .env.example               # Add DATABASE_URL and encryption key
└── app/
    └── services/
        └── auth_service.py    # Replace fake_users_db with database repository
```

### API Changes

#### Enhanced Strava Endpoints
```python
# All Strava endpoints require authentication and resolve current_user automatically

GET /api/strava/status
# Returns: connection status, athlete info, token expiry
# Auth: Required (uses current_user.id)
# Response: {"connected": true, "athlete_id": 12345, "expires_at": "2025-03-20T10:00:00Z"}

DELETE /api/strava/disconnect
# Behavior: 1) Call Strava revoke API, 2) Delete local tokens regardless of external success
# Auth: Required (uses current_user.id)
# Response: {"disconnected": true}

GET /api/strava/activities
# Query params: page (default=1), per_page (default=30, max=100), before, after
# Auth: Required (uses current_user.id)
# Auto-refresh: Refreshes token if within 5 minutes of expiry
# Response: Normalized activity schema (not raw Strava payload)
# Required scopes: activity:read_all
```

#### Authentication Integration
```python
# All Strava routes use existing auth dependency
@router.get("/status")
async def get_strava_status(current_user: User = Depends(get_current_user)):
    # current_user.id resolved from JWT token
    # No user_id accepted from client
    return await strava_service.get_connection_status(current_user.id)

# Same pattern applies to all /api/strava/* endpoints
```

#### Updated Callback Handler
```python
# Secure OAuth flow with state validation
# NOTE: This changes /connect from returning RedirectResponse(302) to JSON {"auth_url": ...}
# The frontend must be updated to handle this — it should read auth_url and redirect the user itself.
@router.get("/connect")
async def connect_strava(current_user: User = Depends(get_current_user)):
    # Requires User.id to be populated from DB (Phase 1 prerequisite)
    state_data = {"user_id": current_user.id, "timestamp": time.time()}
    signed_state = security.sign_data(state_data)  # JWT or HMAC signature
    
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}&"
        f"redirect_uri={STRAVA_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=activity:read_all&"
        f"state={signed_state}&"
        f"approval_prompt=auto"  # Use 'auto' in production; 'force' only for dev/testing
    )
    return {"auth_url": auth_url}

@router.get("/callback")
async def strava_callback(
    code: str, 
    state: str, 
    error: Optional[str] = None
):
    # Validate OAuth state to prevent CSRF
    try:
        state_data = security.verify_signed_data(state)
        user_id = state_data["user_id"]
    except SecurityError:
        raise HTTPException(400, "Invalid OAuth state")
    
    # Exchange code for tokens and store for validated user
    tokens = await exchange_code_for_tokens(code)
    await strava_service.store_tokens(user_id, tokens)
    return RedirectResponse(url=f"{FRONTEND_URL}/settings?strava_connected=true")
```

## Implementation Plan

### ✅ Phase 0: Dependency & Runtime Upgrades (Complete)

> **Why now**: As of April 5 2026, multiple major versions are behind across the full stack. Upgrading before adding new infrastructure is cheaper than migrating later. Versions verified directly from npm and official release pages on this date.

#### Backend Version Targets
| Component | Current | Latest (Apr 5 2026) | Location |
|-----------|---------|---------------------|----------|
| PostgreSQL | `17.7` | `18.3` | `docker-compose-dev.yml`, `docker-compose.yml` |
| Python (Docker image) | `3.13-slim` | `3.14-slim` | `backend/Dockerfile` |
| Python (`pyproject.toml`) | `requires-python = ">=3.9"` | `requires-python = ">=3.14"` | `backend/pyproject.toml` |

#### Frontend Version Targets
| Package | Current | Latest (Apr 5 2026) | Notes |
|---------|---------|---------------------|-------|
| `react` / `react-dom` | `^19.1.0` | `19.2.4` | Minor bump, no breaking changes |
| `react-router-dom` | `^7.7.0` | **Remove** | v7 re-exports from `react-router`; `react-router-dom` is legacy shim |
| `react-router` | not installed | `7.14.0` | Replace `react-router-dom` with this |
| `@types/react-router-dom` | `^5.3.3` | **Remove** | v5 types, wrong for v7; `react-router` v7 ships its own types |
| `vite` | `^7.0.4` | `8.0.3` | **Major** — check migration guide |
| `@vitejs/plugin-react` | `^4.6.0` | `6.0.1` | **Major** — must match Vite 8 |
| `typescript` | `~5.8.3` | `6.0.2` | **Major** — check breaking changes |
| `eslint` | `^9.30.1` | `10.2.0` | **Major** — check config compatibility |
| `prettier` | `^3.6.2` | `3.8.1` | Minor bump |
| `typescript-eslint` | `^8.35.1` | `8.58.0` | Minor bump |

#### Library Replacements Required for Python 3.14

Two production dependencies are **unmaintained** and incompatible with the Python 3.14 upgrade path:

1. **`passlib` → `pwdlib` (or `bcrypt` directly)**
   - `passlib` has not been maintained since 2020. `bcrypt>=5.0.0` (which has explicit Python 3.14 support) broke passlib's package detection.
   - The project currently pins `bcrypt>=3.2.0,<4.0.0` in `pyproject.toml` specifically to work around this — that pin must be removed.
   - **Replacement**: Use `pwdlib[bcrypt]` (actively maintained passlib successor) or call `bcrypt` directly. Either removes the passlib dependency entirely.
   - **Impact**: `AuthService.verify_password`, `AuthService.get_password_hash`, and the `CryptContext` setup in `app/services/auth_service.py` must be updated.

2. **`python-jose` → `PyJWT`**
   - `python-jose` last released 2023, has open CVEs, and is effectively abandoned (FastAPI's own docs now recommend `PyJWT` as the replacement).
   - **Replacement**: `PyJWT>=2.8.0` with `cryptography` as backend (already being added in Phase 1).
   - **Impact**: `AuthService.create_access_token`, `AuthService.verify_token`, and all `from jose import ...` imports in `app/services/auth_service.py` must be updated to `import jwt` (PyJWT).
   - **API contract unchanged**: JWT token structure (`sub`, `exp`) stays identical — only the signing/decoding library changes.

#### Backend Steps
1. **`docker-compose-dev.yml`**: `image: postgres:17.7` → `image: postgres:18.3`
2. **`docker-compose.yml`**: `image: postgres:17.7` → `image: postgres:18.3` (same change, second compose file)
3. **`backend/Dockerfile`**: `FROM python:3.13-slim` → `FROM python:3.14-slim`
4. **`frontend/Dockerfile`**: Already `node:24-alpine` ✅ — no change needed
5. **Replace `passlib`**: Remove `passlib` and update bcrypt pin to `bcrypt>=4.0.0`. Rewrite password hashing in `auth_service.py` using `pwdlib[bcrypt]` or `bcrypt` directly.
6. **Replace `python-jose`**: Remove `python-jose[cryptography]`, add `PyJWT>=2.8.0`. Update all JWT signing/decoding code in `auth_service.py`.
7. **Update `pyproject.toml`**: Bump `requires-python`, remove replaced libraries, add new ones.
8. **Run existing test suite**: Confirm all auth tests pass with the new libraries before proceeding to Phase 1. The existing unit and integration tests in `tests/` cover the auth flow and serve as the regression gate.

#### Node / npm
| Component | Current (Dockerfile) | Latest (Apr 5 2026) | Status |
|-----------|---------------------|---------------------|--------|
| Node.js | `node:24-alpine` | `24.14.1` LTS | ✅ Current — no change needed |
| npm | unpinned (ships with Node 24) | `11.12.1` | ✅ No action needed |

No version bump required. However, Node version is not pinned for local development — no `.nvmrc` or `engines` field exists. Add both as part of Phase 0 to prevent version drift across environments.

#### Frontend Steps
1. **Add `.nvmrc` and `engines` field**: Create `frontend/.nvmrc` containing `24`. Add `"engines": { "node": ">=24" }` to `frontend/package.json`. This pins local dev to match the Docker image.
2. **Replace `react-router-dom` with `react-router`**: Remove `react-router-dom` and `@types/react-router-dom` from `package.json`. Add `react-router@7.14.0`. All source files already import from `'react-router-dom'` — do a project-wide find-and-replace of `'react-router-dom'` → `'react-router'` across all `.tsx`/`.ts` files. The API is identical; only the package name changes.
3. **Bump minor packages**: Update `react`/`react-dom` → `19.2.4`, `prettier` → `3.8.1`, `typescript-eslint` → `8.58.0`.
4. **Upgrade Vite 7 → 8 and `@vitejs/plugin-react` 4 → 6**: Review the [Vite 8 migration guide](https://vite.dev/guide/migration) before upgrading. Update `vite.config.ts` if any deprecated options are used.
5. **Upgrade TypeScript 5 → 6**: Review [TypeScript 6 breaking changes](https://devblogs.microsoft.com/typescript/) before upgrading. Run `tsc --noEmit` to surface any type errors introduced by the new version.
6. **Upgrade ESLint 9 → 10**: Review [ESLint 10 migration guide](https://eslint.org/docs/latest/use/migrate-to-10.0.0). ESLint 10 drops Node 18 support — confirm Node version in CI/local is ≥20.
7. **Run frontend type-check and lint**: `npm run check-all` must pass cleanly before proceeding.

#### Updated `package.json` dependencies (after Phase 0)
```json
{
  "dependencies": {
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "react-router": "^7.14.0"
  },
  "devDependencies": {
    "@eslint/js": "^10.2.0",
    "@types/react": "^19.1.8",
    "@types/react-dom": "^19.1.6",
    "@vitejs/plugin-react": "^6.0.1",
    "eslint": "^10.2.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.20",
    "globals": "^16.3.0",
    "prettier": "^3.8.1",
    "typescript": "^6.0.2",
    "typescript-eslint": "^8.58.0",
    "vite": "^8.0.3"
  }
}
```

#### Updated `pyproject.toml` dependencies (after Phase 0)
```toml
dependencies = [
    "fastapi>=0.116.0",
    "uvicorn>=0.32.0",
    "PyJWT>=2.8.0",           # Replaces python-jose
    "pwdlib[bcrypt]>=0.2.0",  # Replaces passlib + bcrypt pin
    "python-dotenv>=1.0.1",
    "email-validator>=2.1.0",
    "httpx>=0.28.0",
]
```

### ✅ Phase 1: Database Foundation (Complete)
1. **Dependencies**: Add SQLAlchemy, Alembic, cryptography, psycopg2-binary to `pyproject.toml`
2. **Database Setup**: Create `database.py` with async SQLAlchemy engine (`create_async_engine`), `AsyncSession`, and `async_sessionmaker`. All DB calls are natively async — no `asyncio.to_thread()` needed. See ADR `2026-04-17-async-sqlalchemy-migration.md`.
3. **Base Models**: Implement `models/base.py` with timezone-aware timestamps and auto-updating `updated_at`. Fix `UserInDB.created_at` / `updated_at` default from `datetime.utcnow` (deprecated, timezone-naive) to `datetime.now(timezone.utc)`.
4. **Migration Setup**: Initialize Alembic with proper configuration at backend root level
5. **User Table**: Create users table with proper indexes and constraints
6. **Add `id` to Pydantic `User` model**: Add `id: int` to the `User` model in `app/models/user.py`. This is a **hard dependency for Phase 2** — `current_user.id` is used throughout Strava token storage and cannot be resolved until this field exists. Also update `get_current_user` in `app/auth/dependencies.py` to populate it from the DB row. **Note**: Implemented as `id: Optional[int]` — must be tightened to `id: int` (non-optional) as the first step of Phase 2.
7. **Auth Migration**: Replace `fake_users_db` with database repository, maintain same API contract. JWT `sub` claim remains `email` — no change to token structure.
8. **Create `.env.example` files**: Create `backend/.env.example` and root `.env.example` with all required placeholder variables (neither file currently exists).

### ✅ Phase 2: Strava Token Storage (Complete)
1. **Pre-check — `User.id` type**: `app/schemas/user.py` declares `id: int` (non-optional) ✅
2. **Token Model**: `models/strava_token.py` created with one-to-one constraints, FK, and `strava_athlete_id` ✅
3. **Alembic Migrations**: `ead4347b116f_create_strava_tokens_table.py` + `5216de56eb03_add_strava_athlete_id_column.py` generated and applied ✅
4. **Encryption**: `utils/security.py` with Fernet encryption ✅
5. **Repository Layer**: `repositories/strava_token_repository.py` with async CRUD ✅
6. **Service Layer**: `services/strava_service.py` with token storage and refresh logic ✅
7. **`/connect` endpoint**: Returns `{"auth_url": ...}` JSON with `Depends(get_current_user)` and signed state param ✅
8. **Storage Integration**: `/api/strava/callback` no longer uses `get_current_user` — identifies user via signed state param, stores tokens + athlete_id ✅
9. **State signing security**: HMAC key is server-side only (`_STATE_HMAC_KEY` from env), never embedded in the state payload. State format: `{user_id}:{timestamp}:{HMAC-SHA256(key, user_id:timestamp)}` ✅
10. **Cleaned up**: Removed unused `decrypt_token`/`encrypt_token` imports from router; removed dead `generate_strava_auth_url()` code; `hmac`/`hashlib` at module level ✅

### Phase 3: Token Management & API (1.5 hours)
1. **Token Refresh Logic**: Implement automatic refresh with 5-minute safety window
2. **Status Endpoint**: Add `/api/strava/status` with connection status and expiry info
3. **Disconnect Endpoint**: Add `/api/strava/disconnect` with Strava revoke API call
4. **Activities Endpoint**: Add `/api/strava/activities` with pagination and normalized response schema
5. **Error Handling**: Proper handling of revoked tokens and refresh failures

### Phase 4: Testing & Documentation (1 hour)
1. **Critical Path Tests**: OAuth flow, token refresh, disconnect, activities fetch
2. **Migration Tests**: Database upgrade/downgrade smoke testing
3. **Integration Tests**: End-to-end Strava integration with mocked external APIs
4. **Documentation**: Update API docs and setup instructions

## Dependencies

### New Dependencies
```toml
# Add to pyproject.toml dependencies
"sqlalchemy>=2.0.0",
"alembic>=1.13.0", 
"psycopg2-binary>=2.9.0",  # PostgreSQL driver
"cryptography>=42.0.0",   # For Fernet token encryption
```

### Environment Variables
```bash
# Create root .env.example (file does not currently exist):
POSTGRES_DB=your_postgres_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
FRONTEND_URL=http://cycloveda.local

# Create backend/.env.example (file does not currently exist):
DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@postgres:5432/your_postgres_db
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REDIRECT_URI=http://api.cycloveda.local/api/strava/callback

# Generate Fernet key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Value must be a URL-safe base64-encoded 32-byte key, NOT a raw string
STRAVA_ENCRYPTION_KEY=your_fernet_base64_key_here

SECRET_KEY=your_jwt_secret_key
```

### Database Configuration Decisions
- **ORM Mode**: Async SQLAlchemy with `AsyncEngine` + `AsyncSession` + `asyncpg` driver
- **Async boundary**: All DB calls are natively async — no `asyncio.to_thread()` needed
- **Session Management**: `async_sessionmaker` with `async with` context manager per request
- **Migration Tool**: Alembic at backend root level, running through async engine via `run_sync`
- **Driver**: `asyncpg` only — `psycopg2-binary` removed
- **Timestamps**: Timezone-aware (TIMESTAMP WITH TIME ZONE).

## Security Considerations

### Token Storage (Implementation Details)
- **Fields Encrypted**: `access_token_encrypted`, `refresh_token_encrypted` only
- **Fields Unencrypted**: `user_id`, `strava_athlete_id`, `expires_at`, `scope`, timestamps
- **Encryption Method**: Fernet symmetric encryption (cryptography library)
- **Key Management**: Single active app key via `STRAVA_ENCRYPTION_KEY` env var (32 bytes)
- **Key Rotation**: Future work - current design assumes single key
- **Search**: No deterministic search needed on encrypted fields

### Database Security
- Use database connection pooling
- Implement proper transaction handling
- Add database connection timeouts

### Token Refresh Lifecycle (Implementation Details)
```python
# Refresh logic implemented in strava_service.py
async def get_valid_token(user_id: int) -> StravaToken:
    token = await get_token(user_id)
    
    # Refresh if within 5-minute safety window
    if token.expires_at <= datetime.now(timezone.utc) + timedelta(minutes=5):
        try:
            new_tokens = await refresh_strava_token(token.refresh_token)
            await update_token(user_id, new_tokens)
            return await get_token(user_id)  # Reload updated token
        except StravaRefreshError:
            # Token revoked/invalid - mark as disconnected
            await delete_token(user_id)
            raise TokenRevokedError("Strava connection revoked, please reconnect")
    
    return token
```

**Refresh Behavior:**
- **Safety Window**: 5 minutes before expiry
- **Persistence**: Update access_token, refresh_token, expires_at on each refresh
- **Failure Handling**: Delete local tokens on refresh failure, require reconnect
- **Connection Status**: Inferred from token existence and validity

## Testing Strategy

### Critical Path Testing (Implementation-Ready)
- **OAuth Flow**: `/connect` → state generation → `/callback` → token storage
- **OAuth State Validation**: Invalid/expired state handling
- **Token Refresh**: Near-expiry refresh success and failure scenarios  
- **Token Revocation**: Refresh failure handling and cleanup
- **Disconnect Flow**: Strava revoke call + local token deletion
- **Activities Fetch**: Valid token and pre-refresh scenarios
- **Database Migration**: Schema upgrade/downgrade smoke tests

### Test Data Management
- Separate test database (different PostgreSQL database)
- Test fixtures for encrypted Strava tokens
- Mock external Strava API calls with httpx MockTransport
- Test encryption keys separate from production

## Migration Strategy

### User Migration Strategy (Implementation Details)
**Current State**: In-memory `fake_users_db` with 2 test users
**Migration Approach**: 
- **Development Bootstrap**: Create seed migration for test users in dev environment only
- **Production**: No users to migrate (in-memory only)
- **Database Table**: Create users table with proper constraints and indexes
- **Auth API**: Maintain exact same request/response contracts
- **Repository Pattern**: Replace `fake_users_db` lookups with database repository

**Implementation:**
```python
# Development seed migration (dev environment only)
def seed_dev_users():
    """Seed development database with test users"""
    test_users = [
        {"email": "admin@cycloveda.com", "username": "admin", "password": "password"},
        {"email": "user@example.com", "username": "user", "password": "password"}
    ]
    # Insert with proper password hashing
```

**Backwards Compatibility**: 
- Keep same `/api/auth/login` and `/api/auth/me` endpoints
- Same JWT token structure and validation
- No breaking changes to frontend auth logic

### Docker Integration
- **Existing Setup**: PostgreSQL already running in Docker Compose
- **Network Access**: Backend can connect via `postgres:5432` hostname
- **Volume Persistence**: `postgres-data` volume ensures data persistence
- **Health Checks**: Database health already monitored

### Future Migration Path
- PostgreSQL scaling (read replicas, connection pooling)
- Database optimization and indexing
- Backup and restore strategies

## Success Criteria

### Functional Success
- ✅ Strava tokens persist across server restarts
- ✅ Token refresh works automatically with 5-minute safety window
- ✅ Users can connect/disconnect Strava accounts (one-to-one relationship enforced)
- ✅ Existing authentication remains functional (same API contracts)
- ✅ OAuth state validation prevents CSRF attacks
- ✅ Token encryption protects sensitive data at rest

### Technical Success
- ✅ Database migrations work reliably (upgrade/downgrade)
- ✅ Critical path testing covers all token flows
- ✅ No performance regression on existing endpoints
- ✅ Clean architecture patterns maintained (repositories, services, models)
- ✅ Async SQLAlchemy integration matches current FastAPI patterns
- ✅ Timezone-aware timestamps ensure accurate token expiry logic

### Operational Success
- ✅ PostgreSQL containers include persistent data volume
- ✅ Database backups can be created/restored via pg_dump
- ✅ Development environment setup remains simple (seed users for dev)
- ✅ Documentation is complete and implementation-ready

## Risks & Mitigations

### Technical Risks
- **Database Lock Issues**: Use proper connection pooling
- **Token Encryption Loss**: Secure key management strategy
- **Migration Failures**: Comprehensive testing and rollback procedures

### Operational Risks
- **Data Loss**: Regular PostgreSQL backups via pg_dump
- **Performance Impact**: Monitor query performance and connection pooling
- **Docker Network Issues**: Ensure proper container networking configuration

## Timeline

**Total Estimated Time**: 8-9 hours

**Phase Breakdown**:
- Phase 0: Dependency & Runtime Upgrades - 2.5 hours (backend library replacements + frontend major version bumps)
- Phase 1: Database Foundation - 2 hours
- Phase 2: Strava Token Storage - 1.5 hours
- Phase 3: Token Management & API - 1.5 hours
- Phase 4: Testing & Documentation - 1 hour

**Dependencies**: Phase 0 must complete and all tests pass before Phase 1 begins.

## Next Steps

1. **Approve Specification**: Review and approve this technical specification
2. **Environment Setup**: Add dependencies and environment variables
3. **Database Foundation**: Implement Phase 1 of the plan
4. **Progressive Implementation**: Complete remaining phases
5. **Testing & Validation**: Comprehensive testing before deployment

---

**Version**: 1.0  
**Created**: 2025-03-15  
**Author**: Cyclo Veda Development Team  
**Status**: Implementation-Ready

## Critical Decisions Made

### Architecture Decisions
1. **Database**: PostgreSQL (existing container) with async SQLAlchemy (`AsyncEngine` + `AsyncSession` + `asyncpg`)
2. **Encryption**: Fernet encryption for access/refresh tokens only. Key must be base64-encoded (use `Fernet.generate_key()`).
3. **Relationship**: One-to-one user-to-Strava account mapping
4. **Auth Integration**: Use existing JWT auth dependency, resolve `current_user.id`. `id` is populated from the DB row by `get_current_user`. **Phase 2 pre-check**: tighten `id: Optional[int]` → `id: int` in `app/schemas/user.py` before writing any token storage code.
5. **OAuth Security**: Signed state parameter to prevent CSRF. State carries `user_id` (integer) — only valid after Phase 1 DB migration assigns stable user IDs.
6. **Repository Pattern**: Separate repository layer for database operations
7. **Async boundary**: All database operations use native async SQLAlchemy (`AsyncSession`). No `asyncio.to_thread()` wrapping is needed — the async migration was completed as part of Phase 1. See ADR `2026-04-17-async-sqlalchemy-migration.md`.

### API Design Decisions
1. **Disconnect Behavior**: Call Strava revoke API, then delete local tokens
2. **Activities Response**: Normalized schema (not raw Strava payload)
3. **Token Refresh**: 5-minute safety window with automatic retry
4. **Error Handling**: Clean separation between token errors and API errors

### Implementation Decisions
1. **Migration Strategy**: Seed dev users, no production migration needed
2. **File Structure**: Alembic at backend root, repositories for data access
3. **Testing Focus**: Critical path testing over coverage percentage
4. **Backwards Compatibility**: Maintain exact same auth API contracts

### Future Considerations
1. **Key Rotation**: Future work (single key for v1)
2. **Scaling**: PostgreSQL read replicas when needed
3. **Monitoring**: Token refresh success/failure metrics
4. **Security**: Consider connection status field for better UX
5. **`approval_prompt`**: Currently hardcoded as `force` in both the existing router and spec examples. Change to `auto` for production to avoid forcing re-authorization on every connect attempt.
6. **Async SQLAlchemy**: Completed ahead of Phase 2. The `asyncio.to_thread()` workaround has been removed. All DB operations use native `AsyncSession` via `asyncpg`. See ADR `2026-04-17-async-sqlalchemy-migration.md`.
