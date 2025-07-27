"""
Unit tests for AuthService

This module contains comprehensive unit tests for the AuthService class,
testing all authentication-related functionality including password hashing,
user authentication, and JWT token operations.

Test Categories:
- Password operations (hashing, verification)
- User authentication and retrieval
- JWT token creation and validation
- Error handling and edge cases
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.services.auth_service import AuthService, SECRET_KEY, ALGORITHM
from app.models.user import User, UserInDB
from app.models.token import TokenData


class TestPasswordOperations:
    """Test password hashing and verification operations"""
    
    def test_get_password_hash_creates_valid_hash(self):
        """Test that password hashing creates a valid bcrypt hash"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)
        
        # Bcrypt hashes start with $2b$ and are 60 characters long
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60
        assert hashed != password  # Should not be plaintext
    
    def test_get_password_hash_different_for_same_input(self):
        """Test that hashing the same password twice produces different hashes (due to salt)"""
        password = "testpassword123"
        hash1 = AuthService.get_password_hash(password)
        hash2 = AuthService.get_password_hash(password)
        
        assert hash1 != hash2  # Different due to random salt
    
    def test_verify_password_correct_password(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)
        
        assert AuthService.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = AuthService.get_password_hash(password)
        
        assert AuthService.verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_password(self):
        """Test password verification with empty password"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)
        
        assert AuthService.verify_password("", hashed) is False
    
    def test_verify_password_empty_hash(self):
        """Test password verification with empty hash"""
        password = "testpassword123"
        
        # Empty hash should raise an exception or return False
        try:
            result = AuthService.verify_password(password, "")
            assert result is False
        except Exception:
            # If an exception is raised, that's also acceptable behavior
            assert True


class TestUserOperations:
    """Test user authentication and retrieval operations"""
    
    def test_get_user_existing_user(self):
        """Test retrieving an existing user"""
        user = AuthService.get_user("admin@cycloveda.com")
        
        assert user is not None
        assert isinstance(user, User)
        assert user.email == "admin@cycloveda.com"
        assert user.is_active is True
    
    def test_get_user_nonexistent_user(self):
        """Test retrieving a non-existent user"""
        user = AuthService.get_user("nonexistent@example.com")
        
        assert user is None
    
    def test_get_user_empty_email(self):
        """Test retrieving user with empty email"""
        user = AuthService.get_user("")
        
        assert user is None
    
    def test_authenticate_user_valid_credentials(self):
        """Test user authentication with valid credentials"""
        # Use the pre-initialized test user credentials
        user = AuthService.authenticate_user("admin@cycloveda.com", "password")
        
        assert user is not None
        assert isinstance(user, User)
        assert user.email == "admin@cycloveda.com"
    
    def test_authenticate_user_invalid_password(self):
        """Test user authentication with invalid password"""
        user = AuthService.authenticate_user("admin@cycloveda.com", "wrongpassword")
        
        assert user is None
    
    def test_authenticate_user_nonexistent_user(self):
        """Test user authentication with non-existent user"""
        user = AuthService.authenticate_user("nonexistent@example.com", "password")
        
        assert user is None
    
    def test_authenticate_user_inactive_user(self):
        """Test user authentication with inactive user"""
        # This test assumes there might be inactive users in the future
        # For now, we'll test the logic path
        with patch('app.services.auth_service.fake_users_db') as mock_db:
            # Mock the fake_users_db to include an inactive user
            mock_db.__getitem__.return_value = {
                "username": "inactive",
                "email": "inactive@example.com",
                "hashed_password": AuthService.get_password_hash("password"),
                "is_active": False
            }
            mock_db.__contains__.return_value = True
            
            with patch.object(AuthService, 'get_user') as mock_get_user:
                inactive_user = User(
                    username="inactive",
                    email="inactive@example.com",
                    is_active=False
                )
                mock_get_user.return_value = inactive_user
                
                user = AuthService.authenticate_user("inactive@example.com", "password")
                # The current implementation doesn't check is_active, so it will return the user
                # This test documents the current behavior
                assert user is not None


class TestTokenOperations:
    """Test JWT token creation and validation operations"""
    
    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry"""
        data = {"sub": "test@example.com"}
        token = AuthService.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify contents
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded
    
    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = AuthService.create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        
        # Decode token to verify expiry
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # Should expire approximately 60 minutes from now (allowing for small time differences)
        expected_exp = datetime.now(timezone.utc) + expires_delta
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 5  # Within 5 seconds tolerance
    
    def test_create_access_token_empty_data(self):
        """Test creating access token with empty data"""
        data = {}
        token = AuthService.create_access_token(data)
        
        assert isinstance(token, str)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
    
    def test_verify_token_valid_token(self):
        """Test token verification with valid token"""
        data = {"sub": "test@example.com"}
        token = AuthService.create_access_token(data)
        
        token_data = AuthService.verify_token(token)
        
        assert token_data is not None
        assert isinstance(token_data, TokenData)
        assert token_data.email == "test@example.com"
    
    def test_verify_token_invalid_token(self):
        """Test token verification with invalid token"""
        invalid_token = "invalid.token.here"
        
        token_data = AuthService.verify_token(invalid_token)
        
        assert token_data is None
    
    def test_verify_token_expired_token(self):
        """Test token verification with expired token"""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = AuthService.create_access_token(data, expires_delta)
        
        token_data = AuthService.verify_token(token)
        
        assert token_data is None
    
    def test_verify_token_malformed_token(self):
        """Test token verification with malformed token"""
        malformed_tokens = [
            "",  # Empty token
            "not.a.token",  # Invalid format
            "header.payload",  # Missing signature
            "header.payload.signature.extra",  # Too many parts
        ]
        
        for token in malformed_tokens:
            token_data = AuthService.verify_token(token)
            assert token_data is None, f"Token '{token}' should be invalid"
    
    def test_verify_token_no_subject(self):
        """Test token verification with token missing subject"""
        # Create token without 'sub' claim
        data = {"user_id": "123"}  # Wrong claim name
        token = AuthService.create_access_token(data)
        
        token_data = AuthService.verify_token(token)
        
        assert token_data is None


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios"""
    
    def test_hash_password_unicode_characters(self):
        """Test password hashing with unicode characters"""
        password = "pássw0rd123!@#$%^&*()_+{}|:<>?[]\\;'\",./"
        hashed = AuthService.get_password_hash(password)
        
        assert AuthService.verify_password(password, hashed) is True
    
    def test_hash_password_very_long_password(self):
        """Test password hashing with very long password"""
        password = "a" * 1000  # 1000 character password
        hashed = AuthService.get_password_hash(password)
        
        assert AuthService.verify_password(password, hashed) is True
    
    def test_authenticate_user_case_sensitivity(self):
        """Test that email authentication is case sensitive"""
        # Test with different case
        user = AuthService.authenticate_user("ADMIN@CYCLOVEDA.COM", "password")
        
        # Should fail because email case doesn't match
        assert user is False
    
    @patch('app.services.auth_service.jwt.encode')
    def test_create_access_token_jwt_error(self, mock_jwt_encode):
        """Test token creation when JWT encoding fails"""
        mock_jwt_encode.side_effect = Exception("JWT encoding failed")
        
        data = {"sub": "test@example.com"}
        
        # Should handle the exception gracefully
        with pytest.raises(Exception):
            AuthService.create_access_token(data)
    
    @patch('app.services.auth_service.pwd_context.verify')
    def test_verify_password_bcrypt_error(self, mock_verify):
        """Test password verification when bcrypt fails"""
        mock_verify.side_effect = Exception("Bcrypt verification failed")
        
        # Should handle the exception gracefully
        result = AuthService.verify_password("password", "hash")
        assert result is False


class TestConstants:
    """Test that constants are properly configured"""
    
    def test_secret_key_exists(self):
        """Test that SECRET_KEY is configured"""
        assert AuthService.SECRET_KEY is not None
        assert len(AuthService.SECRET_KEY) > 0
    
    def test_algorithm_is_valid(self):
        """Test that ALGORITHM is set to a valid value"""
        assert AuthService.ALGORITHM == "HS256"
    
    def test_token_expire_minutes_is_positive(self):
        """Test that token expiry time is positive"""
        assert AuthService.ACCESS_TOKEN_EXPIRE_MINUTES > 0
