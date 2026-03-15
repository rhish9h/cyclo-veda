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

### Existing Assets
- ✅ OAuth flow implemented (`/api/strava/connect`, `/api/strava/callback`)
- ✅ Token exchange logic (`exchange_code_for_tokens()`)
- ✅ Clean architecture patterns (models, services, routers)
- ✅ Environment configuration structure
- ✅ Comprehensive testing framework

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
- **Already Available**: PostgreSQL 17.7 container in both docker-compose.yml and docker-compose-dev.yml
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
@router.get("/connect")
async def connect_strava(current_user: User = Depends(get_current_user)):
    # Generate signed state containing user_id
    state_data = {"user_id": current_user.id, "timestamp": time.time()}
    signed_state = security.sign_data(state_data)  # JWT or HMAC signature
    
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}&"
        f"redirect_uri={STRAVA_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=activity:read_all&"
        f"state={signed_state}&"
        f"approval_prompt=force"
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

### Phase 1: Database Foundation (2 hours)
1. **Dependencies**: Add SQLAlchemy, Alembic, cryptography, psycopg2-binary to `pyproject.toml`
2. **Database Setup**: Create `database.py` with sync SQLAlchemy engine and session management
3. **Base Models**: Implement `models/base.py` with timezone-aware timestamps and auto-updating `updated_at`
4. **Migration Setup**: Initialize Alembic with proper configuration at backend root level
5. **User Table**: Create users table with proper indexes and constraints
6. **Auth Migration**: Replace `fake_users_db` with database repository, maintain same API contract

### Phase 2: Strava Token Storage (1.5 hours)
1. **Token Model**: Create `models/strava_token.py` with one-to-one constraints and encrypted fields
2. **Encryption**: Implement `utils/security.py` with Fernet encryption for access/refresh tokens only
3. **Repository Layer**: Create `repositories/strava_token_repository.py` with CRUD operations
4. **Service Layer**: Implement `services/strava_service.py` with token storage and refresh logic
5. **Storage Integration**: Update `/api/strava/callback` to validate state and store encrypted tokens

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
# Already in .env.example:
POSTGRES_DB=your_postgres_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password

# Add to backend/.env.example:
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
STRAVA_ENCRYPTION_KEY=your_fernet_encryption_key_32_bytes
```

### Database Configuration Decisions
- **ORM Mode**: Sync SQLAlchemy (simpler, matches current FastAPI patterns)
- **Session Management**: Context-local sessions with proper cleanup
- **Migration Tool**: Alembic at backend root level
- **Timestamps**: Timezone-aware (TIMESTAMP WITH TIME ZONE)

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
- ✅ Sync SQLAlchemy integration matches current FastAPI patterns
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

**Total Estimated Time**: 5-6 hours

**Phase Breakdown**:
- Phase 1: Database Foundation - 2 hours
- Phase 2: Strava Token Storage - 1.5 hours  
- Phase 3: Token Management & API - 1.5 hours
- Phase 4: Testing & Documentation - 1 hour

**Dependencies**: None - can start immediately

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
1. **Database**: PostgreSQL (existing container) with sync SQLAlchemy
2. **Encryption**: Fernet encryption for access/refresh tokens only
3. **Relationship**: One-to-one user-to-Strava account mapping
4. **Auth Integration**: Use existing JWT auth dependency, resolve current_user.id
5. **OAuth Security**: Signed state parameter to prevent CSRF
6. **Repository Pattern**: Separate repository layer for database operations

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
