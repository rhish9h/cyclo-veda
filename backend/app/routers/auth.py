"""Authentication router module for Cyclo Veda.

This module defines the authentication endpoints for the API including:
- User login and token generation
- Current user information retrieval
- Protected route access
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth.dependencies import get_current_active_user
from ..models.user import User, UserLogin
from ..models.token import Token
from ..services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES

# Router configuration
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Authentication failed"},
        422: {"description": "Validation error"},
    },
)

@router.post(
    "/login",
    response_model=Token,
    summary="User Login",
    description="Authenticate user with email and password, returns JWT access token",
    responses={
        200: {"description": "Login successful, returns access token"},
        401: {"description": "Invalid credentials"},
    },
)
async def login_for_access_token(user_login: UserLogin) -> Token:
    """Authenticate user and return JWT access token.
    
    This endpoint validates user credentials and returns a JWT token
    that can be used for subsequent authenticated requests.
    
    Args:
        user_login: User credentials (email and password)
        
    Returns:
        Token: JWT access token and token type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Authenticate user with provided credentials
    user = AuthService.authenticate_user(user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token with configured expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=User,
    summary="Get Current User",
    description="Retrieve information about the currently authenticated user",
    responses={
        200: {"description": "Current user information"},
        401: {"description": "Not authenticated or invalid token"},
    },
)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current authenticated user information.
    
    This endpoint returns the profile information of the currently
    authenticated user based on the provided JWT token.
    
    Args:
        current_user: Injected current user from JWT token
        
    Returns:
        User: Current user's profile information
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    return current_user
