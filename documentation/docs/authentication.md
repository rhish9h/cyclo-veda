# Authentication System

## Overview
The Cyclo Veda application uses JWT (JSON Web Token) based authentication. This document outlines the authentication flow, endpoints, and security considerations.

## Authentication Flow

1. **Login**
   - Client sends email and password to `/api/auth/login`
   - Server validates credentials and returns a JWT token
   - Token is stored client-side (HTTP-only cookie recommended)

2. **Accessing Protected Routes**
   - Client sends token in `Authorization: Bearer <token>` header
   - Server validates token and grants access if valid

## Endpoints

### Login
- **URL**: `POST /api/auth/login`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```

### Get Current User
- **URL**: `GET /api/auth/me`
- **Headers**:
  ```
  Authorization: Bearer <token>
  ```
- **Response**:
  ```json
  {
    "email": "user@example.com",
    "username": "testuser",
    "is_active": true
  }
  ```

## Security Considerations

### Token Storage
- **Recommended**: HTTP-only, Secure, SameSite=Strict cookies
- **Alternative**: `localStorage` (less secure against XSS)

### Password Security
- Passwords are hashed using bcrypt with 12 rounds
- Passwords are never stored in plaintext

### Token Security
- Token expiration: 30 minutes
- Algorithm: HS256
- Secret key is stored in environment variables

## Error Handling

### Common Errors
- `401 Unauthorized`: Invalid or missing token
- `422 Unprocessable Entity`: Validation error in request
- `400 Bad Request`: Malformed request

## Rate Limiting
(To be implemented)
- 100 requests per minute per IP for login attempts
- 1000 requests per minute for authenticated endpoints
