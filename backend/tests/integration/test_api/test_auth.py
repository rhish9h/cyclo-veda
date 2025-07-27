"""
Integration tests for authentication API endpoints

This module contains integration tests for the authentication API,
testing complete HTTP request/response cycles and authentication workflows.

Test Categories:
- Login endpoint testing
- Token validation endpoint testing
- Protected endpoint access
- Authentication error scenarios
- Complete authentication flows
"""

import pytest
from fastapi.testclient import TestClient

from main import app


class TestAuthLogin:
    """Test /auth/login endpoint integration"""
    
    def test_login_success_with_valid_credentials(self, client):
        """Test successful login with valid credentials"""
        login_data = {
            "email": "admin@cycloveda.com",
            "password": "password"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Should return access token
        assert "access_token" in response_data
        assert "token_type" in response_data
        assert response_data["token_type"] == "bearer"
        assert isinstance(response_data["access_token"], str)
        assert len(response_data["access_token"]) > 0
    
    def test_login_failure_with_invalid_email(self, client):
        """Test login failure with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data
    
    def test_login_failure_with_invalid_password(self, client):
        """Test login failure with incorrect password"""
        login_data = {
            "email": "admin@cycloveda.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data
    
    def test_login_with_missing_email(self, client):
        """Test login with missing email field"""
        login_data = {
            "password": "password"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_missing_password(self, client):
        """Test login with missing password field"""
        login_data = {
            "email": "admin@cycloveda.com"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_invalid_email_format(self, client):
        """Test login with invalid email format"""
        login_data = {
            "email": "invalid-email-format",
            "password": "password"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        # Returns 401 because UserLogin uses str (not EmailStr) for case-sensitive auth
        # Invalid email formats are treated as authentication failures, not validation errors
        assert response.status_code == 401
    
    def test_login_with_empty_credentials(self, client):
        """Test login with empty credentials"""
        login_data = {
            "email": "",
            "password": ""
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        # Returns 401 because empty credentials are treated as authentication failures
        # not validation errors (since UserLogin uses str for case-sensitive auth)
        assert response.status_code == 401


class TestAuthMe:
    """Test /auth/me endpoint integration"""
    
    def test_get_current_user_with_valid_token(self, client, valid_token):
        """Test getting current user info with valid token"""
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Should return user information
        assert "email" in response_data
        assert "username" in response_data
        assert "is_active" in response_data
        assert response_data["email"] == "user@example.com"
    
    def test_get_current_user_without_token(self, client):
        """Test getting current user info without authentication token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data
    
    def test_get_current_user_with_invalid_token(self, client):
        """Test getting current user info with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data
    
    def test_get_current_user_with_expired_token(self, client, expired_token):
        """Test getting current user info with expired token"""
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data
    
    def test_get_current_user_with_malformed_auth_header(self, client):
        """Test getting current user info with malformed authorization header"""
        malformed_headers = [
            {"Authorization": "invalid_format_token"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "NotBearer token"},  # Wrong scheme
            {"Authorization": "Bearer token1 token2"},  # Multiple tokens
        ]
        
        for headers in malformed_headers:
            response = client.get("/api/auth/me", headers=headers)
            assert response.status_code == 401


class TestCompleteAuthFlow:
    """Test complete authentication workflows"""
    
    def test_complete_login_and_access_protected_resource(self, client):
        """Test complete flow: login -> get token -> access protected resource"""
        # Step 1: Login to get token
        login_data = {
            "email": "admin@cycloveda.com",
            "password": "password"
        }
        
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Step 2: Use token to access protected resource
        headers = {"Authorization": f"Bearer {access_token}"}
        
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        user_data = me_response.json()
        assert user_data["email"] == "admin@cycloveda.com"
    
    def test_login_with_different_users(self, client):
        """Test login with different user accounts"""
        test_users = [
            {"email": "admin@cycloveda.com", "password": "password"},
            {"email": "user@example.com", "password": "password"}
        ]
        
        for user_creds in test_users:
            response = client.post("/api/auth/login", json=user_creds)
            assert response.status_code == 200
            
            token_data = response.json()
            assert "access_token" in token_data
            
            # Verify token works
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            me_response = client.get("/api/auth/me", headers=headers)
            assert me_response.status_code == 200
            
            user_data = me_response.json()
            assert user_data["email"] == user_creds["email"]


class TestAuthErrorHandling:
    """Test authentication error handling scenarios"""
    
    def test_login_endpoint_method_not_allowed(self, client):
        """Test that login endpoint only accepts POST requests"""
        login_data = {
            "email": "admin@cycloveda.com",
            "password": "password"
        }
        
        # Test other HTTP methods
        response_get = client.get("/api/auth/login")
        assert response_get.status_code == 405  # Method Not Allowed
        
        response_put = client.put("/api/auth/login", json=login_data)
        assert response_put.status_code == 405  # Method Not Allowed
        
        response_delete = client.delete("/api/auth/login")
        assert response_delete.status_code == 405  # Method Not Allowed
    
    def test_me_endpoint_method_not_allowed(self, client, valid_token):
        """Test that /me endpoint only accepts GET requests"""
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Test other HTTP methods
        response_post = client.post("/api/auth/me", headers=headers)
        assert response_post.status_code == 405  # Method Not Allowed
        
        response_put = client.put("/api/auth/me", headers=headers)
        assert response_put.status_code == 405  # Method Not Allowed
        
        response_delete = client.delete("/api/auth/me", headers=headers)
        assert response_delete.status_code == 405  # Method Not Allowed
    
    def test_invalid_json_in_login_request(self, client):
        """Test login with invalid JSON payload"""
        # Send invalid JSON
        response = client.post(
            "/api/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_content_type_validation(self, client):
        """Test that endpoints validate content type"""
        login_data = {
            "email": "admin@cycloveda.com",
            "password": "password"
        }
        
        # Send as form data instead of JSON
        response = client.post("/api/auth/login", data=login_data)
        
        # Should still work or return appropriate error
        assert response.status_code in [200, 422]  # Depends on FastAPI configuration


class TestAuthSecurity:
    """Test authentication security aspects"""
    
    def test_password_not_returned_in_responses(self, client):
        """Test that passwords are never returned in API responses"""
        login_data = {
            "email": "admin@cycloveda.com",
            "password": "password"
        }
        
        # Login response should not contain password
        login_response = client.post("/api/auth/login", json=login_data)
        login_data_response = login_response.json()
        
        assert "password" not in str(login_data_response).lower()
        assert "hashed_password" not in str(login_data_response).lower()
        
        # Get token and check user info response
        if login_response.status_code == 200:
            token = login_data_response["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            me_response = client.get("/api/auth/me", headers=headers)
            me_data = me_response.json()
            
            assert "password" not in str(me_data).lower()
            assert "hashed_password" not in str(me_data).lower()
    
    def test_token_format_and_structure(self, client):
        """Test that returned tokens have expected format"""
        login_data = {
            "email": "admin@cycloveda.com",
            "password": "password"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            
            # JWT tokens should have 3 parts separated by dots
            token_parts = access_token.split(".")
            assert len(token_parts) == 3
            
            # Each part should be base64-encoded (non-empty)
            for part in token_parts:
                assert len(part) > 0
    
    def test_case_sensitive_email_authentication(self, client):
        """Test that email authentication is case sensitive"""
        # Test with different case variations
        email_variations = [
            "ADMIN@CYCLOVEDA.COM",
            "Admin@CycloVeda.Com",
            "admin@CYCLOVEDA.COM"
        ]
        
        for email in email_variations:
            login_data = {
                "email": email,
                "password": "password"
            }
            
            response = client.post("/api/auth/login", json=login_data)
            # Should fail because email case doesn't match exactly
            assert response.status_code == 401
