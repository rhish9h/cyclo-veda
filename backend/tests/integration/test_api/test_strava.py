"""True integration tests for /api/strava/* endpoints.

Each test uses:
- A real PostgreSQL session (via the real_db fixture in tests/integration/conftest.py)
  wrapped in a rolled-back transaction so the DB is pristine after every test.
- An httpx.AsyncClient with ASGITransport pointing at the live FastAPI app.
- get_current_user overridden with a fixed User (no JWT roundtrip needed).
- Only outbound HTTP calls to strava.com are mocked — everything else is real.

Run via docker-compose.test.yml which provides the DATABASE_URL.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.repositories.strava_token_repository import strava_token_repository
from app.services.strava_service import store_tokens


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _future(minutes: int = 60) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def _raw_tokens(
    access: str = "raw_access",
    refresh: str = "raw_refresh",
    expires_in: int = 21600,
    athlete_id: int = 42,
) -> dict:
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "scope": "activity:read_all",
        "athlete": {"id": athlete_id},
    }


def _strava_activity(activity_id: int = 1) -> dict:
    return {
        "id": activity_id,
        "name": "Morning Ride",
        "sport_type": "Ride",
        "start_date": "2025-04-01T07:00:00Z",
        "distance": 30000.0,
        "moving_time": 3600,
        "elapsed_time": 3700,
        "total_elevation_gain": 200.0,
        "average_speed": 8.3,
        "max_speed": 12.0,
        "kudos_count": 5,
        "achievement_count": 2,
        "athlete_count": 1,
        "map": {"summary_polyline": "abc123"},
    }


# ---------------------------------------------------------------------------
# GET /api/strava/connect
# ---------------------------------------------------------------------------


class TestConnect:
    async def test_returns_auth_url_with_signed_state(self, async_client, integration_user):
        """Endpoint builds a Strava OAuth URL embedding a signed state for the user."""
        response = await async_client.get("/api/strava/connect")

        assert response.status_code == 200
        body = response.json()
        assert "auth_url" in body
        assert "strava.com/oauth/authorize" in body["auth_url"]
        assert f"state=" in body["auth_url"]

    async def test_requires_authentication(self, async_client):
        """Without a valid user the endpoint returns 401."""
        from app.auth.dependencies import get_current_user
        from app.main import app
        from fastapi import HTTPException

        def _raise_401():
            raise HTTPException(status_code=401, detail="Not authenticated")

        app.dependency_overrides[get_current_user] = _raise_401
        try:
            response = await async_client.get("/api/strava/connect")
            assert response.status_code == 401
        finally:
            app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# GET /api/strava/callback
# ---------------------------------------------------------------------------


class TestCallback:
    async def test_redirects_on_strava_error_param(self, async_client):
        response = await async_client.get(
            "/api/strava/callback",
            params={"error": "access_denied"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "error=strava_auth_failed" in response.headers["location"]

    async def test_redirects_on_missing_code(self, async_client):
        response = await async_client.get(
            "/api/strava/callback",
            params={"state": "bad_state"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "error=" in response.headers["location"]

    async def test_redirects_on_invalid_state(self, async_client):
        response = await async_client.get(
            "/api/strava/callback",
            params={"code": "somecode", "state": "tampered_state"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "error=strava_invalid_state" in response.headers["location"]

    async def test_stores_token_in_db_on_valid_callback(
        self, async_client, real_db, integration_user
    ):
        """Full happy path: valid state + mocked Strava HTTP → token row created in DB."""
        from app.routers import strava as strava_router

        valid_state = strava_router._sign_state(integration_user.id)
        strava_response = _raw_tokens(access="acc_tok", refresh="ref_tok", athlete_id=99)

        with patch(
            "app.routers.strava._exchange_code_for_tokens",
            new_callable=AsyncMock,
            return_value=strava_response,
        ):
            response = await async_client.get(
                "/api/strava/callback",
                params={"code": "valid_code", "state": valid_state},
                follow_redirects=False,
            )

        assert response.status_code == 302
        assert "strava_connected=true" in response.headers["location"]

        # Verify the token row was actually written to the DB
        record = await strava_token_repository.get_by_user_id(real_db, integration_user.id)
        assert record is not None
        assert record.strava_athlete_id == 99


# ---------------------------------------------------------------------------
# GET /api/strava/status
# ---------------------------------------------------------------------------


class TestStatus:
    async def test_returns_connected_false_when_no_token(self, async_client, real_db):
        """Fresh DB has no token row — endpoint reports not connected."""
        response = await async_client.get("/api/strava/status")

        assert response.status_code == 200
        assert response.json()["connected"] is False

    async def test_returns_connected_true_when_token_exists(
        self, async_client, real_db, integration_user
    ):
        """After storing a token the endpoint reports connected with correct metadata."""
        await store_tokens(real_db, integration_user.id, _raw_tokens(athlete_id=42))

        response = await async_client.get("/api/strava/status")

        assert response.status_code == 200
        body = response.json()
        assert body["connected"] is True
        assert body["athlete_id"] == 42
        assert body["has_refresh_token"] is True

    async def test_is_expiring_soon_flag(self, async_client, real_db, integration_user):
        """Token expiring in 2 minutes sets is_expiring_soon=True."""
        tokens = _raw_tokens()
        tokens["expires_in"] = 120  # 2 minutes
        await store_tokens(real_db, integration_user.id, tokens)

        response = await async_client.get("/api/strava/status")

        assert response.json()["is_expiring_soon"] is True

    async def test_not_expiring_soon_with_plenty_of_time(
        self, async_client, real_db, integration_user
    ):
        """Token expiring in 6 hours does not set is_expiring_soon."""
        await store_tokens(real_db, integration_user.id, _raw_tokens(expires_in=21600))

        response = await async_client.get("/api/strava/status")

        assert response.json()["is_expiring_soon"] is False


# ---------------------------------------------------------------------------
# DELETE /api/strava/disconnect
# ---------------------------------------------------------------------------


class TestDisconnect:
    async def test_returns_404_when_not_linked(self, async_client, real_db):
        """No token in DB → 404, deleted=False."""
        with patch("app.routers.strava.httpx.AsyncClient"):
            response = await async_client.delete("/api/strava/disconnect")

        assert response.status_code == 404
        assert response.json()["deleted"] is False

    async def test_deletes_token_from_db(self, async_client, real_db, integration_user):
        """After disconnect the token row is gone from the DB."""
        await store_tokens(real_db, integration_user.id, _raw_tokens())

        # Best-effort Strava revoke call — mock so we don't hit the network
        with patch("app.services.strava_service.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_http.post = AsyncMock(return_value=MagicMock(status_code=200))
            mock_cls.return_value = mock_http

            response = await async_client.delete("/api/strava/disconnect")

        assert response.status_code == 200
        assert response.json()["deleted"] is True

        # DB row must be gone
        record = await strava_token_repository.get_by_user_id(real_db, integration_user.id)
        assert record is None


# ---------------------------------------------------------------------------
# GET /api/strava/activities
# ---------------------------------------------------------------------------


class TestActivities:
    async def test_returns_401_when_no_token_in_db(self, async_client, real_db):
        """No token row → get_valid_token raises TokenRevokedError → 401."""
        response = await async_client.get("/api/strava/activities")
        assert response.status_code == 401

    async def test_returns_normalized_activities(
        self, async_client, real_db, integration_user
    ):
        """Token in DB + mocked Strava HTTP → normalized activities returned."""
        await store_tokens(real_db, integration_user.id, _raw_tokens())

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [_strava_activity(1), _strava_activity(2)]

        with patch("app.routers.strava.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_http.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_http

            response = await async_client.get("/api/strava/activities")

        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 2
        assert body["activities"][0]["name"] == "Morning Ride"
        assert body["activities"][0]["distance_meters"] == 30000.0

    async def test_returns_502_when_strava_api_errors(
        self, async_client, real_db, integration_user
    ):
        """Token exists but Strava returns 500 → endpoint returns 502."""
        await store_tokens(real_db, integration_user.id, _raw_tokens())

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("app.routers.strava.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_http.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_http

            response = await async_client.get("/api/strava/activities")

        assert response.status_code == 502

    async def test_pagination_params_forwarded_to_strava(
        self, async_client, real_db, integration_user
    ):
        """page and per_page query params are forwarded to the Strava API call."""
        await store_tokens(real_db, integration_user.id, _raw_tokens())

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch("app.routers.strava.httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_http.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = mock_http

            response = await async_client.get("/api/strava/activities?page=3&per_page=50")

        assert response.status_code == 200
        call_kwargs = mock_http.get.call_args.kwargs
        assert call_kwargs["params"]["page"] == 3
        assert call_kwargs["params"]["per_page"] == 50
