"""Token-related Pydantic schemas for authentication.

This module defines the data structures used for:
- JWT token responses
- Token data storage and validation
- Authentication token handling

Naming convention:
- This file is a Pydantic schema (validation/serialization).
- SQLAlchemy ORM models live in app/models/.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str = Field(
        ...,
        description="JWT access token for authentication"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (typically 'bearer')"
    )
    expires_in: Optional[int] = Field(
        default=None,
        description="Token expiration time in seconds"
    )
    refresh_token: Optional[str] = Field(
        default=None,
        description="Optional refresh token for token renewal"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "def456..."
            }
        }


class TokenData(BaseModel):
    """Data stored in JWT token payload."""
    email: Optional[EmailStr] = Field(
        default=None,
        description="User email from token subject"
    )
    scopes: List[str] = Field(
        default_factory=list,
        description="Token scopes/permissions"
    )
    exp: Optional[datetime] = Field(
        default=None,
        description="Token expiration timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "scopes": ["read", "write"],
                "exp": "2024-01-01T12:00:00Z"
            }
        }
