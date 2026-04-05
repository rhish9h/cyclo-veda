"""Authentication service module for Cyclo Veda.

This module provides authentication and authorization services including:
- Password hashing and verification
- JWT token creation and validation
- User authentication and retrieval via the database repository

All user-lookup methods accept a SQLAlchemy Session so they are testable
in isolation (mock the session / repository) and work inside async FastAPI
handlers via asyncio.to_thread().
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy.orm import Session

from ..schemas.user import User
from ..schemas.token import TokenData
from ..repositories.user_repository import user_repository

# Configuration constants
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_TOKEN_EXPIRE_MINUTES = 15

# Password hashing configuration
pwd_hasher = PasswordHash([BcryptHasher()])


class AuthService:
    """Service class for handling authentication operations.

    Provides static methods for:
    - Password hashing and verification
    - User authentication and retrieval (database-backed)
    - JWT token creation and validation
    """

    # Class constants for test access
    SECRET_KEY = SECRET_KEY
    ALGORITHM = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

    # ------------------------------------------------------------------
    # Password operations
    # ------------------------------------------------------------------

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hashed password.

        Args:
            plain_password: The plaintext password to verify
            hashed_password: The hashed password to verify against

        Returns:
            bool: True if password matches, False otherwise or if verification fails
        """
        try:
            return pwd_hasher.verify(plain_password, hashed_password)
        except Exception:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password for secure storage.

        Args:
            password: The plaintext password to hash

        Returns:
            str: The hashed password
        """
        return pwd_hasher.hash(password)

    # ------------------------------------------------------------------
    # User operations (database-backed)
    # ------------------------------------------------------------------

    @staticmethod
    def get_user(db: Session, email: str) -> Optional[User]:
        """Retrieve a user by email address from the database.

        Args:
            db: Active database session
            email: The user's email address (case-sensitive)

        Returns:
            Optional[User]: Pydantic User schema if found, None otherwise
        """
        row = user_repository.get_by_email(db, email)
        if row is None:
            return None
        return User(
            id=row.id,
            email=row.email,
            username=row.username,
            is_active=row.is_active,
        )

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        """Authenticate a user with email and password.

        Args:
            db: Active database session
            email: The user's email address (case-sensitive)
            password: The user's plaintext password

        Returns:
            User: Pydantic User schema if authentication successful
            False: If authentication fails (user not found or wrong password)
        """
        row = user_repository.get_by_email(db, email)
        if row is None:
            return False
        if not AuthService.verify_password(password, row.hashed_password):
            return False
        return User(
            id=row.id,
            email=row.email,
            username=row.username,
            is_active=row.is_active,
        )

    # ------------------------------------------------------------------
    # Token operations
    # ------------------------------------------------------------------

    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token.

        Args:
            data: The data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            str: The encoded JWT token
        """
        to_encode = data.copy()
        utc_now = datetime.now(timezone.utc)
        expire = utc_now + (expires_delta or timedelta(minutes=DEFAULT_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token.

        Args:
            token: The JWT token to verify

        Returns:
            Optional[TokenData]: Token data if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            return TokenData(email=email)
        except InvalidTokenError:
            return None
