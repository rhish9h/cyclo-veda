# API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints except `/` and `/api/auth/login` require authentication.

Include the JWT token in the `Authorization` header:
```
Authorization: Bearer <your_token>
```

## Endpoints

### Health Check
```
GET /
```
**Response**
```json
{
  "message": "Welcome to Cyclo Veda API",
  "status": "healthy",
  "version": "0.1.0"
}
```

### Authentication

#### Login
```
POST /api/auth/login
```
**Request Body**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```
GET /api/auth/me
```
**Headers**
```
Authorization: Bearer <token>
```

**Response**
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "is_active": true
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

## Rate Limiting
(To be implemented)
- 100 requests per minute per IP for login attempts
- 1000 requests per minute for authenticated endpoints

## Response Headers
- `Content-Type: application/json`
- `X-Request-ID`: Unique ID for each request (for debugging)
