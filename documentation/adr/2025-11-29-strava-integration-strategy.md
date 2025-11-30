# Strava API Integration Strategy

**Date:** 2025-11-29
**Status:** Accepted

## Context

To provide value to cyclists, Cyclo Veda needs to analyze their activity data. The primary source of this data is Strava. We need a secure and efficient way to authenticate users with Strava and retrieve their activity data.

The integration requires:
1.  Secure authentication (OAuth 2.0).
2.  Asynchronous data fetching to not block the API.
3.  Secure management of API credentials (Client ID/Secret).

## Decision

We have decided to implement the Strava integration using the following strategy:

### 1. Backend-for-Frontend (BFF) OAuth Flow
We will implement the OAuth 2.0 Authorization Code flow where the backend handles the token exchange.
- **Frontend**: Redirects user to Backend `/connect` endpoint.
- **Backend**: Redirects user to Strava's authorization page.
- **Strava**: Redirects user back to Backend `/callback` endpoint with a code.
- **Backend**: Exchanges code for access/refresh tokens using `httpx` and redirects user back to Frontend with status/tokens (or stores them).

This ensures the `STRAVA_CLIENT_SECRET` is never exposed to the client browser.

### 2. Async HTTP Client (`httpx`)
We chose `httpx` over `requests` or `aiohttp` because:
- It offers a modern, type-hinted API that is very similar to `requests`.
- It provides native `async`/`await` support, which integrates perfectly with FastAPI's async path operations.
- It supports both HTTP/1.1 and HTTP/2.

### 3. Scope Management
We will request `activity:read_all` scope to ensure we can fetch all necessary activity data for analysis.

## Consequences

### Positive
- **Security**: Client secrets remain on the server.
- **Performance**: Async HTTP calls prevent blocking the main thread during third-party API requests.
- **Maintainability**: `httpx` is a modern, well-maintained library.

### Negative
- **New Dependency**: Adds `httpx` to the project dependencies.
- **Complexity**: Requires managing token lifecycle (access token expiration and refresh tokens), which needs to be implemented in the data persistence layer.

## Future Considerations
- Implement background tasks (using Celery or FastAPI BackgroundTasks) for fetching historical activities to avoid timeout during the callback.
- Implement webhook handling for real-time updates from Strava.
