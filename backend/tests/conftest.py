"""
Pytest configuration and shared fixtures for Cyclo Veda Backend tests

This file contains:
- Pytest configuration settings
- Shared fixtures used across multiple test files
- Test database setup and teardown
- Mock objects and test utilities
- Authentication helpers for testing protected endpoints

Usage:
- Fixtures defined here are automatically available in all test files
- Use @pytest.fixture for reusable test components
- Follow naming convention: test_* for test functions, *_fixture for fixtures
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch
import os
from datetime import datetime, timedelta
from jose import jwt

# Import your app components
from main import app
from app.services.auth_service import AuthService
from app.models.user import User, UserCreate
from app.auth.dependencies import get_current_user


@pytest.fixture
def client():
    """
    FastAPI test client fixture
    
    Provides a test client for making HTTP requests to the FastAPI application.
    This client can be used for integration tests of API endpoints.
    
    Returns:
        TestClient: Configured test client for the FastAPI app
    """
    return TestClient(app)


@pytest.fixture
def auth_service():
    """
    AuthService instance fixture
    
    Provides a fresh instance of AuthService for testing.
    
    Returns:
        AuthService: Fresh AuthService instance
    """
    return AuthService()


@pytest.fixture
def mock_user():
    """
    Mock user fixture for testing
    
    Provides a consistent test user object for use in tests.
    
    Returns:
        User: Test user object with known properties
    """
    return User(
        email="user@example.com",  # Must match email in fake_users_db
        username="testuser",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        is_active=True
    )


@pytest.fixture
def mock_user_create():
    """
    Mock user creation data fixture
    
    Provides test data for user creation operations.
    
    Returns:
        UserCreate: Test user creation data
    """
    return UserCreate(
        email="newuser@example.com",
        password="testpassword123"
    )


@pytest.fixture
def valid_token(mock_user):
    """
    Valid JWT token fixture for testing authenticated endpoints
    
    Creates a valid JWT token for the mock user that can be used
    to test protected endpoints.
    
    Args:
        mock_user: User object to create token for
        
    Returns:
        str: Valid JWT token
    """
    # Use the same secret key as your app
    from app.services.auth_service import SECRET_KEY, ALGORITHM
    
    # Create token data
    expire = datetime.utcnow() + timedelta(minutes=30)
    token_data = {
        "sub": mock_user.email,
        "exp": expire
    }
    
    # Generate token
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token


@pytest.fixture
def expired_token(mock_user):
    """
    Expired JWT token fixture for testing token validation
    
    Creates an expired JWT token to test token expiration handling.
    
    Args:
        mock_user: User object to create token for
        
    Returns:
        str: Expired JWT token
    """
    # Import from auth service to ensure consistency
    from app.services.auth_service import SECRET_KEY, ALGORITHM
    
    # Create expired token data
    expire = datetime.utcnow() - timedelta(minutes=30)  # Already expired
    token_data = {
        "sub": mock_user.email,
        "exp": expire
    }
    
    # Generate expired token
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token


@pytest.fixture
def authenticated_client(client, valid_token):
    """
    Authenticated test client fixture
    
    Provides a test client with authentication headers set.
    Useful for testing protected endpoints.
    
    Args:
        client: FastAPI test client
        valid_token: Valid JWT token
        
    Returns:
        TestClient: Test client with authentication headers
    """
    client.headers.update({"Authorization": f"Bearer {valid_token}"})
    return client


@pytest.fixture
def mock_auth_dependency(mock_user):
    """
    Mock authentication dependency fixture
    
    Mocks the get_current_user dependency to return a test user
    without requiring actual authentication. Useful for unit tests
    of protected endpoints.
    
    Args:
        mock_user: User object to return from dependency
        
    Yields:
        Mock: Mocked dependency function
    """
    def mock_get_current_user():
        return mock_user
    
    # Override the dependency
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield mock_get_current_user
    
    # Clean up after test
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_environment():
    """
    Reset environment variables before each test
    
    Ensures tests start with a clean environment state.
    This fixture runs automatically before each test.
    """
    # Store original environment
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment after test
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_login_data():
    """
    Sample login data fixture
    
    Provides consistent login data for testing authentication endpoints.
    
    Returns:
        dict: Login credentials
    """
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def invalid_login_data():
    """
    Invalid login data fixture
    
    Provides invalid login data for testing authentication failure scenarios.
    
    Returns:
        dict: Invalid login credentials
    """
    return {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }


# Pytest configuration
def pytest_configure(config):
    """
    Pytest configuration hook
    
    Sets up pytest configuration and custom markers.
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Custom pytest markers for test organization
pytest_plugins = []
