# Async SQLAlchemy Migration

**Date:** 2026-04-17  
**Status:** Implemented  
**Impact:** High

## Context

The Cyclo Veda backend was using synchronous SQLAlchemy with `asyncio.to_thread()` wrappers to avoid blocking the event loop in FastAPI route handlers. This approach had several drawbacks:

1. **Thread-safety concerns**: SQLAlchemy sync sessions are not thread-safe, and sessions crossed thread boundaries between dependency injection and route handlers
2. **Boilerplate overhead**: Every database call required manual `asyncio.to_thread()` wrapping, with no compile-time enforcement
3. **Maintenance burden**: Easy to forget the wrapper, leading to event loop blocking under load
4. **Inconsistent patterns**: Mixed sync/async code across the codebase

## Decision

Migrate the entire database layer to native async SQLAlchemy:

- **Engine**: `create_engine` -> `create_async_engine` with `asyncpg` driver
- **Session**: `Session` -> `AsyncSession` with `async_sessionmaker`
- **Repository methods**: All CRUD operations converted to `async def` with `select()` API
- **Service layer**: User authentication methods made async
- **Dependencies**: FastAPI dependency injection updated to use `AsyncSession`
- **Migrations**: Alembic configured to run through async engine via `run_sync`

## Consequences

### Positive
- **Performance**: Native async operations without thread switching overhead
- **Safety**: No thread-safety concerns with session objects
- **Clarity**: All database operations are explicitly async (`await` required)
- **Maintainability**: Compile-time signals if async operations are missed
- **Consistency**: Uniform async patterns across the entire codebase

### Negative
- **Breaking change**: All database-dependent methods required signature updates
- **Learning curve**: Team needs to understand async SQLAlchemy patterns
- **Lazy loading**: SQLAlchemy's default lazy loading doesn't work with async sessions (requires explicit `selectinload`/`joinedload` for relationships)
- **Migration complexity**: Alembic requires special async configuration

### Neutral
- **Driver change**: `psycopg2-binary` -> `asyncpg` (both maintained, asyncpg is faster)
- **URL prefix**: `postgresql://` -> `postgresql+asyncpg://` in environment variables
- **Query style**: ORM queries changed from `db.query(Model)` to `await db.execute(select(Model))`

## Implementation Details

### Files Changed
- `pyproject.toml`: Replaced `psycopg2-binary` with `asyncpg>=0.30.0`
- `app/database.py`: Full async engine and session setup
- `migrations/env.py`: Async migration runner with `run_sync`
- `app/repositories/user_repository.py`: All methods async with `select()` API
- `app/services/auth_service.py`: User lookup methods async
- `app/auth/dependencies.py`: Removed `asyncio.to_thread()` wrappers
- `app/routers/auth.py`: Direct async calls to service layer
- `backend/.env.example`: Updated DATABASE_URL prefix

### Migration Strategy
1. **Dependency update**: Switch to asyncpg driver
2. **Database layer**: Convert engine, session, and repository patterns
3. **Service layer**: Update authentication methods
4. **Route handlers**: Remove thread wrappers, use direct async calls
5. **Environment**: Update connection string format
6. **Testing**: Verify all auth flows work with new patterns

### Database URL Changes
```bash
# Before
DATABASE_URL=postgresql://user:pass@host:5432/db

# After  
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
```

### Query Pattern Changes
```python
# Before (sync)
def get_user(db: Session, email: str):
    return db.query(UserORM).filter(UserORM.email == email).first()

# After (async)
async def get_user(db: AsyncSession, email: str):
    result = await db.execute(select(UserORM).filter(UserORM.email == email))
    return result.scalar_one_or_none()
```

## Future Considerations

1. **Relationship loading**: Future model relationships will need explicit loading strategies
2. **Performance monitoring**: Track async operation performance under load
3. **Connection pooling**: May need async-specific pool tuning
4. **Testing patterns**: Async test fixtures may need updates for complex scenarios

## Status

**Completed**: 2026-04-17  
**Impact**: All authentication and user management endpoints now use native async database operations. The foundation is in place for Phase 2 Strava token storage to be built on async patterns from the start.
