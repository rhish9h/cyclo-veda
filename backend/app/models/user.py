"""User models for authentication and authorization.

This module defines the core user data structures:
- UserBase: Common fields shared across user models
- UserLogin: Login credentials for authentication
- UserInDB: Complete user record with sensitive data (database storage)
- User: Safe user representation for API responses (excludes sensitive data)
- UserCreate: User registration data (future use)
- UserResponse: Extended user data with timestamps (future use)

Security Note:
- UserInDB contains hashed_password (excluded from serialization)
- User model excludes all sensitive information for safe API responses
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

# Constants for field constraints
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 8


class UserBase(BaseModel):
    """Base user model containing common user fields.
    
    This is an abstract base class that defines the core user attributes
    shared across all user models. Not used directly - only for inheritance.
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
    """Model for creating a new user (registration).
    
    Used for user registration endpoints. Includes password validation.
    Currently not used - will be needed when registration is implemented.
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
        """Validate password meets minimum requirements.
        
        Args:
            v: The password string to validate
            
        Returns:
            str: The validated password
            
        Raises:
            ValueError: If password doesn't meet minimum length requirement
        """
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password must be at least {PASSWORD_MIN_LENGTH} characters')
            
        # Add more password strength checks as needed
        # Example: require numbers, special chars, etc.
        return v


class UserLogin(BaseModel):
    """Model for user login credentials.
    
    Used by the /auth/login endpoint to validate user credentials.
    Contains only the fields needed for authentication.
    
    Currently used in: app.routers.auth.login_for_access_token
    """
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="securePassword123!")


class UserInDB(UserBase):
    """Database user model with sensitive information.
    
    Complete user record as stored in the database. Contains all user data
    including sensitive fields like hashed_password (excluded from serialization).
    
    Security: hashed_password has exclude=True to prevent accidental exposure.
    
    Currently used in: app.services.auth_service (internal operations only)
    """
    hashed_password: str = Field(..., exclude=True)  # Never include in responses
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    roles: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2
        json_schema_extra = {  # Updated from schema_extra for Pydantic V2
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "is_active": True,
                "is_superuser": False,
                "roles": ["user"]
            }
        }


class User(UserBase):
    """Standard user model for API responses (excludes sensitive data).
    
    Safe representation of user data for public API responses. Excludes all
    sensitive information like passwords, timestamps, and internal flags.
    
    Security: Contains only fields safe for external consumption.
    
    Currently used in:
    - app.auth.dependencies (authentication functions)
    - app.routers.auth.get_current_user_info (API response)
    """
    is_active: bool = Field(default=True)
    roles: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2
        json_schema_extra = {  # Updated from schema_extra for Pydantic V2
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "is_active": True,
                "roles": ["user"]
            }
        }


class UserResponse(UserBase):
    """Extended user model for detailed API responses.
    
    Includes additional metadata like ID, timestamps, and detailed user info.
    Intended for admin endpoints or detailed user profile views.
    
    Currently not used - reserved for future admin/profile features.
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str]

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2



