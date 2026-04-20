"""Repository for Strava token storage and retrieval.

Provides database-backed CRUD operations for StravaTokenORM records
using async SQLAlchemy sessions.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strava_token import StravaTokenORM


class StravaTokenRepository:
    """Data access object for StravaOAuthToken records."""

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> Optional[StravaTokenORM]:
        """Retrieve a token record for a specific user.

        Args:
            db: Active async database session
            user_id: The user's database primary key

        Returns:
            StravaTokenORM or None if no record exists
        """
        stmt = select(StravaTokenORM).where(StravaTokenORM.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update(
        db: AsyncSession,
        user_id: int,
        access_token: str,
        refresh_token: str,
        token_type: str,
        expires_in: int,
        expires_at: datetime,
        scope: str,
        strava_athlete_id: Optional[int] = None,
    ) -> StravaTokenORM:
        """Insert or update a token record for the given user.

        Args:
            db: Active async database session
            user_id: The user's database primary key
            access_token: Raw access token string
            refresh_token: Raw refresh token string
            token_type: e.g., "Bearer"
            expires_in: Token lifetime in seconds from Strava
            expires_at: UTC expiration datetime
            scope: Strava permission scopes
            strava_athlete_id: Strava athlete ID

        Returns:
            Updated or created StravaTokenORM instance
        """
        record = await StravaTokenRepository.get_by_user_id(db, user_id)
        if record:
            record.access_token = access_token
            record.refresh_token = refresh_token
            record.token_type = token_type
            record.expires_in = expires_in
            record.expires_at = expires_at
            record.scope = scope
            record.strava_athlete_id = strava_athlete_id
            record.updated_at = datetime.now(timezone.utc)
        else:
            record = StravaTokenORM(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                expires_in=expires_in,
                expires_at=expires_at,
                scope=scope,
                strava_athlete_id=strava_athlete_id,
            )
            db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def delete_by_user_id(db: AsyncSession, user_id: int) -> bool:
        """Delete a token record for a specific user.

        Args:
            db: Active async database session
            user_id: The user's database primary key

        Returns:
            True if a record was deleted, False if none existed
        """
        record = await StravaTokenRepository.get_by_user_id(db, user_id)
        if record:
            del_record = StravaTokenORM
            result = await db.execute(select(del_record).where(del_record.user_id == user_id))
            existing = result.scalar_one_or_none()
            if existing:
                await db.delete(existing)
                await db.commit()
                return True
        return False


# Export singleton instance for convenience in services
strava_token_repository = StravaTokenRepository()
