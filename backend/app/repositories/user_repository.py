"""User repository - database CRUD operations for the users table.

All methods are async (async SQLAlchemy). Can be called directly
from async FastAPI route handlers:

    user = await user_repository.get_by_email(db, email)
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import UserORM


class UserRepository:
    """Database access layer for the users table."""

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[UserORM]:
        """Fetch a user row by email address (case-sensitive).

        Args:
            db: Active database session
            email: Exact email address to look up

        Returns:
            UserORM row if found, None otherwise
        """
        result = await db.execute(
            select(UserORM).filter(UserORM.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[UserORM]:
        """Fetch a user row by primary key.

        Args:
            db: Active database session
            user_id: Integer primary key

        Returns:
            UserORM row if found, None otherwise
        """
        result = await db.execute(
            select(UserORM).filter(UserORM.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[UserORM]:
        """Fetch a user row by username (case-sensitive).

        Args:
            db: Active database session
            username: Exact username to look up

        Returns:
            UserORM row if found, None otherwise
        """
        result = await db.execute(
            select(UserORM).filter(UserORM.username == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        email: str,
        username: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> UserORM:
        """Insert a new user row.

        Args:
            db: Active database session
            email: Unique email address
            username: Unique username
            hashed_password: Bcrypt-hashed password (never store plaintext)
            full_name: Optional display name
            is_active: Whether the account is active (default True)
            is_superuser: Whether the account has admin privileges (default False)

        Returns:
            Newly created and committed UserORM row
        """
        user = UserORM(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def set_active(db: AsyncSession, user: UserORM, *, is_active: bool) -> UserORM:
        """Enable or disable a user account.

        Args:
            db: Active database session
            user: UserORM row to update
            is_active: New active state

        Returns:
            Updated UserORM row
        """
        user.is_active = is_active
        await db.commit()
        await db.refresh(user)
        return user


user_repository = UserRepository()
