"""
Unit tests for User models

This module contains comprehensive unit tests for all user-related Pydantic models,
testing validation, serialization, and business logic.

Test Categories:
- UserBase model validation
- UserCreate model validation and password strength
- UserLogin model validation
- UserInDB model with sensitive data handling
- User model for safe API responses
- UserResponse model for extended responses
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from typing import List

from app.models.user import (
    UserBase, UserCreate, UserLogin, UserInDB, User, UserResponse,
    USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH, PASSWORD_MIN_LENGTH
)


class TestUserBase:
    """Test UserBase model validation"""
    
    def test_valid_user_base(self):
        """Test creating UserBase with valid data"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser"
        }
        user = UserBase(**user_data)
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
    
    def test_invalid_email_format(self):
        """Test UserBase with invalid email format"""
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test..test@example.com",
            "test@.com",
            ""
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                UserBase(email=email, username="testuser")
    
    def test_username_length_validation(self):
        """Test username length constraints"""
        valid_email = "test@example.com"
        
        # Test minimum length
        short_username = "a" * (USERNAME_MIN_LENGTH - 1)
        with pytest.raises(ValidationError):
            UserBase(email=valid_email, username=short_username)
        
        # Test maximum length
        long_username = "a" * (USERNAME_MAX_LENGTH + 1)
        with pytest.raises(ValidationError):
            UserBase(email=valid_email, username=long_username)
        
        # Test valid lengths
        min_username = "a" * USERNAME_MIN_LENGTH
        max_username = "a" * USERNAME_MAX_LENGTH
        
        user_min = UserBase(email=valid_email, username=min_username)
        user_max = UserBase(email=valid_email, username=max_username)
        
        assert user_min.username == min_username
        assert user_max.username == max_username
    
    def test_required_fields(self):
        """Test that required fields are enforced"""
        # Missing email
        with pytest.raises(ValidationError):
            UserBase(username="testuser")
        
        # Missing username
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com")


class TestUserCreate:
    """Test UserCreate model validation and password strength"""
    
    def test_valid_user_create(self):
        """Test creating UserCreate with valid data"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "securePassword123!"
        }
        user = UserCreate(**user_data)
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password == "securePassword123!"
    
    def test_password_minimum_length(self):
        """Test password minimum length validation"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "a" * (PASSWORD_MIN_LENGTH - 1)
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "at least" in str(exc_info.value).lower()
    
    def test_password_strength_validation(self):
        """Test custom password strength validation"""
        base_data = {
            "email": "test@example.com",
            "username": "testuser"
        }
        
        # Test valid passwords
        valid_passwords = [
            "a" * PASSWORD_MIN_LENGTH,  # Minimum length
            "securePassword123!",
            "VeryLongPasswordThatIsSecure123456789"
        ]
        
        for password in valid_passwords:
            user = UserCreate(**base_data, password=password)
            assert user.password == password
    
    def test_password_required(self):
        """Test that password field is required"""
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", username="testuser")


class TestUserLogin:
    """Test UserLogin model validation"""
    
    def test_valid_user_login(self):
        """Test creating UserLogin with valid credentials"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        user_login = UserLogin(**login_data)
        
        assert user_login.email == "test@example.com"
        assert user_login.password == "password123"
    
    def test_login_required_fields(self):
        """Test that both email and password are required"""
        # Missing password
        with pytest.raises(ValidationError):
            UserLogin(email="test@example.com")
        
        # Missing email
        with pytest.raises(ValidationError):
            UserLogin(password="password123")
    
    def test_login_email_validation(self):
        """Test email validation in login model"""
        with pytest.raises(ValidationError):
            UserLogin(email="invalid-email", password="password123")


class TestUserInDB:
    """Test UserInDB model with sensitive data handling"""
    
    def test_valid_user_in_db(self):
        """Test creating UserInDB with valid data"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "$2b$12$hashedpassword",
            "is_active": True,
            "is_superuser": False,
            "roles": ["user"]
        }
        user = UserInDB(**user_data)
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "$2b$12$hashedpassword"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.roles == ["user"]
    
    def test_default_values(self):
        """Test default values for optional fields"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "$2b$12$hashedpassword"
        }
        user = UserInDB(**user_data)
        
        assert user.is_active is True  # Default
        assert user.is_superuser is False  # Default
        assert user.roles == []  # Default empty list
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_hashed_password_exclusion(self):
        """Test that hashed_password is excluded from serialization"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "$2b$12$hashedpassword"
        }
        user = UserInDB(**user_data)
        
        # Convert to dict (simulates JSON serialization)
        user_dict = user.model_dump()
        
        # hashed_password should be excluded
        assert "hashed_password" not in user_dict
        assert "email" in user_dict
        assert "username" in user_dict
    
    def test_timestamps_auto_generation(self):
        """Test that timestamps are automatically generated"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "$2b$12$hashedpassword"
        }
        user = UserInDB(**user_data)
        
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)


class TestUser:
    """Test User model for safe API responses"""
    
    def test_valid_user(self):
        """Test creating User with valid data"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "roles": ["user", "admin"]
        }
        user = User(**user_data)
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.roles == ["user", "admin"]
    
    def test_user_default_values(self):
        """Test default values for User model"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser"
        }
        user = User(**user_data)
        
        assert user.is_active is True  # Default
        assert user.roles == []  # Default empty list
    
    def test_user_safe_serialization(self):
        """Test that User model only contains safe fields"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "roles": ["user"]
        }
        user = User(**user_data)
        user_dict = user.model_dump()
        
        # Should contain safe fields
        expected_fields = {"email", "username", "is_active", "roles"}
        assert set(user_dict.keys()) == expected_fields
        
        # Should not contain sensitive fields
        sensitive_fields = {"hashed_password", "created_at", "updated_at", "is_superuser"}
        for field in sensitive_fields:
            assert field not in user_dict


class TestUserResponse:
    """Test UserResponse model for extended responses"""
    
    def test_valid_user_response(self):
        """Test creating UserResponse with valid data"""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "roles": ["user", "admin"]
        }
        user = UserResponse(**user_data)
        
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.roles == ["user", "admin"]
    
    def test_user_response_required_fields(self):
        """Test that required fields are enforced in UserResponse"""
        # Missing id
        with pytest.raises(ValidationError):
            UserResponse(
                email="test@example.com",
                username="testuser",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                roles=[]
            )


class TestModelInteroperability:
    """Test interactions between different user models"""
    
    def test_user_from_user_in_db(self):
        """Test creating User from UserInDB (safe conversion)"""
        user_in_db_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "$2b$12$hashedpassword",
            "is_active": True,
            "roles": ["user"]
        }
        user_in_db = UserInDB(**user_in_db_data)
        
        # Convert to safe User model
        user_data = user_in_db.model_dump(exclude={"hashed_password", "created_at", "updated_at", "is_superuser"})
        user = User(**user_data)
        
        assert user.email == user_in_db.email
        assert user.username == user_in_db.username
        assert user.is_active == user_in_db.is_active
        assert user.roles == user_in_db.roles
    
    def test_user_create_to_user_in_db_simulation(self):
        """Test simulating user creation flow"""
        # Start with UserCreate (registration)
        user_create_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securePassword123!"
        }
        user_create = UserCreate(**user_create_data)
        
        # Simulate creating UserInDB (what would happen in service)
        user_in_db_data = {
            "email": user_create.email,
            "username": user_create.username,
            "hashed_password": "$2b$12$hashedversionof" + user_create.password,  # Simulated hash
            "is_active": True
        }
        user_in_db = UserInDB(**user_in_db_data)
        
        assert user_in_db.email == user_create.email
        assert user_in_db.username == user_create.username
        assert user_in_db.hashed_password != user_create.password  # Should be hashed


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_unicode_in_username(self):
        """Test unicode characters in username"""
        user_data = {
            "email": "test@example.com",
            "username": "tëst_ûsér_123"
        }
        user = UserBase(**user_data)
        assert user.username == "tëst_ûsér_123"
    
    def test_special_characters_in_email(self):
        """Test special characters in email"""
        valid_emails = [
            "test+tag@example.com",
            "test.dot@example.com",
            "test-dash@example.com",
            "test_underscore@example.com"
        ]
        
        for email in valid_emails:
            user = UserBase(email=email, username="testuser")
            assert user.email == email
    
    def test_empty_roles_list(self):
        """Test handling of empty roles list"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "roles": []
        }
        user = User(**user_data)
        assert user.roles == []
    
    def test_large_roles_list(self):
        """Test handling of large roles list"""
        large_roles = [f"role_{i}" for i in range(100)]
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "roles": large_roles
        }
        user = User(**user_data)
        assert len(user.roles) == 100
        assert user.roles == large_roles
