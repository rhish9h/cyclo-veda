"""Authentication service module for Cyclo Veda.

This module provides authentication and authorization services including:
- Password hashing and verification
- JWT token creation and validation
- User authentication and retrieval
- Mock user database (to be replaced with real database in production)
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..models.user import User, UserInDB
from ..models.token import TokenData

# Configuration constants
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_TOKEN_EXPIRE_MINUTES = 15

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mock user database - TODO: Replace with real database in production
fake_users_db: Dict[str, Dict[str, any]] = {}

class AuthService:
    """Service class for handling authentication operations.
    
    This class provides static methods for:
    - Password hashing and verification
    - User authentication and retrieval
    - JWT token creation and validation
    """
    
    # Class constants for test access
    SECRET_KEY = SECRET_KEY
    ALGORITHM = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    
    # Password operations
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against its hash.
        
        Args:
            plain_password: The plaintext password to verify
            hashed_password: The hashed password to compare against
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password for secure storage.
        
        Args:
            password: The plaintext password to hash
            
        Returns:
            str: The hashed password
        """
        return pwd_context.hash(password)
    
    # User operations
    @staticmethod
    def get_user(email: str) -> Optional[User]:
        """Retrieve a user by email address.
        
        Args:
            email: The user's email address
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        if email in fake_users_db:
            user_dict = fake_users_db[email]
            return User(**user_dict)
        return None

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password.
        
        Args:
            email: The user's email address
            password: The user's plaintext password
            
        Returns:
            Optional[User]: User object if authentication successful, None otherwise
        """
        user = AuthService.get_user(email)
        if not user:
            return None
            
        user_dict = fake_users_db[email]
        if not AuthService.verify_password(password, user_dict["hashed_password"]):
            return None
            
        return user
    
    # Token operations
    @staticmethod
    def create_access_token(data: Dict[str, any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token.
        
        Args:
            data: The data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            str: The encoded JWT token
        """
        to_encode = data.copy()
        
        # Use timezone-aware UTC datetime
        utc_now = datetime.now(timezone.utc)
        if expires_delta:
            expire = utc_now + expires_delta
        else:
            expire = utc_now + timedelta(minutes=DEFAULT_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

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
        except JWTError:
            return None


# Mock user database initialization
def _initialize_mock_users() -> None:
    """Initialize the mock user database with test users.
    
    This function creates test users with hashed passwords.
    In production, this should be replaced with proper database seeding.
    """
    # Generate fresh password hash to avoid bcrypt compatibility issues
    test_password_hash = AuthService.get_password_hash("password")
    
    # Test users for development
    test_users = {
        "admin@cycloveda.com": {
            "username": "admin",
            "email": "admin@cycloveda.com",
            "hashed_password": test_password_hash,
            "is_active": True,
        },
        "user@example.com": {
            "username": "testuser",
            "email": "user@example.com",
            "hashed_password": test_password_hash,
            "is_active": True,
        },
    }
    
    fake_users_db.update(test_users)


# Initialize mock users on module import
_initialize_mock_users()
