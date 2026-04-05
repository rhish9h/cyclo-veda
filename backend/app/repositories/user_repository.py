"""User repository — database CRUD operations for the users table.

All methods are synchronous (sync SQLAlchemy). When called from async
FastAPI route handlers, wrap in asyncio.to_thread():

    import asyncio
    user = await asyncio.to_thread(user_repository.get_by_email, db, email)
"""

from typing import Optional

from sqlalchemy.orm import Session

from ..models.user import UserORM


class UserRepository:
    """Database access layer for the users table."""

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[UserORM]:
        """Fetch a user row by email address (case-sensitive).

        Args:
            db: Active database session
            email: Exact email address to look up

        Returns:
            UserORM row if found, None otherwise
        """
        return db.query(UserORM).filter(UserORM.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[UserORM]:
        """Fetch a user row by primary key.

        Args:
            db: Active database session
            user_id: Integer primary key

        Returns:
            UserORM row if found, None otherwise
        """
        return db.query(UserORM).filter(UserORM.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[UserORM]:
        """Fetch a user row by username (case-sensitive).

        Args:
            db: Active database session
            username: Exact username to look up

        Returns:
            UserORM row if found, None otherwise
        """
        return db.query(UserORM).filter(UserORM.username == username).first()

    @staticmethod
    def create(
        db: Session,
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
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def set_active(db: Session, user: UserORM, *, is_active: bool) -> UserORM:
        """Enable or disable a user account.

        Args:
            db: Active database session
            user: UserORM row to update
            is_active: New active state

        Returns:
            Updated UserORM row
        """
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository()
