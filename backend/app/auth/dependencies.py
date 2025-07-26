"""Authentication dependencies for FastAPI routes.

This module provides dependency functions that can be used to protect routes
and access the current authenticated user's information.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..services.auth_service import AuthService
from ..models.user import User

# Constants
AUTH_SCHEME = "Bearer"
INVALID_CREDENTIALS_MESSAGE = "Could not validate credentials"
INACTIVE_USER_MESSAGE = "Inactive user"

# Configure HTTP Bearer token authentication
security = HTTPBearer(
    bearerFormat="JWT",
    description=f"Enter your {AUTH_SCHEME} token",
    auto_error=False,  # We'll handle missing tokens ourselves
)


def _create_credentials_exception(detail: str = INVALID_CREDENTIALS_MESSAGE) -> HTTPException:
    """Create a standardized 401 Unauthorized exception.
    
    Args:
        detail: The error detail message
        
    Returns:
        HTTPException: Configured 401 exception with WWW-Authenticate header
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": AUTH_SCHEME},
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """Dependency to get the current authenticated user from JWT token.
    
    This dependency will:
    1. Check for the presence of an Authorization header
    2. Validate the JWT token
    3. Return the corresponding user if valid
    
    Args:
        credentials: The HTTP Authorization credentials from the request header
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: 401 if token is missing, invalid, or user not found
    """
    if not credentials:
        raise _create_credentials_exception("Missing Authorization header")
        
    if credentials.scheme.lower() != AUTH_SCHEME.lower():
        raise _create_credentials_exception(
            f"Invalid authentication scheme. Expected: {AUTH_SCHEME}"
        )
    
    # Verify token and get user data
    token_data = AuthService.verify_token(credentials.credentials)
    if not token_data:
        raise _create_credentials_exception("Invalid or expired token")
    
    # Get user from database
    user = AuthService.get_user(email=token_data.email)
    if not user:
        raise _create_credentials_exception("User not found")
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get the current active user.
    
    Extends get_current_user to verify the user's account is active.
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        User: The authenticated and active user
        
    Raises:
        HTTPException: 400 if user account is inactive
        HTTPException: 401 if user is not authenticated (from get_current_user)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INACTIVE_USER_MESSAGE,
        )
    return current_user
