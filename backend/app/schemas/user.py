"""User Pydantic schemas for request/response validation.

This module defines the core user data structures used for API validation:
- UserBase: Common fields shared across user schemas
- UserCreate: User registration data (not yet wired to an endpoint)
- UserLogin: Login credentials for the /auth/login endpoint
- User: Safe user representation for API responses

Naming convention:
- This file is a Pydantic schema (validation/serialization).
- SQLAlchemy ORM models live in app/models/user.py.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator

# Constants for field constraints
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 8


class UserBase(BaseModel):
    """Base user schema containing common user fields.
    
    Abstract base class that defines core user attributes shared across all
    user schemas. Not used directly — only for inheritance.
    """
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="User's email address (must be valid email format)"
    )
    username: str = Field(
        ...,
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        example="johndoe",
        description=f"Unique username ({USERNAME_MIN_LENGTH}-{USERNAME_MAX_LENGTH} chars)"
    )


class UserCreate(UserBase):
    """Schema for creating a new user (registration).
    
    Used for user registration endpoints. Includes password validation.
    Currently not used — will be needed when registration is implemented.
    """
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        example="securePassword123!",
        description=f"Password (min {PASSWORD_MIN_LENGTH} characters)"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets minimum requirements."""
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password must be at least {PASSWORD_MIN_LENGTH} characters')
        return v


class UserLogin(BaseModel):
    """Schema for user login credentials.
    
    Used by the /auth/login endpoint to validate user credentials.
    Note: Uses str instead of EmailStr for case-sensitive email authentication.
    
    Currently used in: app.routers.auth.login_for_access_token
    """
    email: str = Field(..., example="user@example.com", description="Email address (case-sensitive)")
    password: str = Field(..., example="securePassword123!")


class User(UserBase):
    """Standard user schema for API responses (excludes sensitive data).
    
    Safe representation of user data for public API responses. Excludes all
    sensitive information like passwords, timestamps, and internal flags.
    
    Security: Contains only fields safe for external consumption.
    
    id is populated from the database row by get_current_user dependency.
    
    Currently used in:
    - app.auth.dependencies (authentication functions)
    - app.routers.auth.get_current_user_info (API response)
    """
    id: Optional[int] = Field(default=None, description="Database primary key")
    is_active: bool = Field(default=True)
    roles: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "is_active": True,
                "roles": ["user"]
            }
        }


