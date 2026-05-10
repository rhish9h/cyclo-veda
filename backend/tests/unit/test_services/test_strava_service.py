"""Unit tests for app/services/strava_service.py

All DB and HTTP calls are mocked — no live services required.
The STRAVA_ENCRYPTION_KEY env var must be set to a valid Fernet key
(provided via .env.test in Docker; falls back to conftest fixture here).
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.strava_service import (
    TokenRevokedError,
    StravaRefreshError,
    get_valid_token,
    revoke_and_delete,
    store_tokens,
)
from app.utils.security import encrypt_token


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _future(minutes: int = 60) -> datetime:
    """Return a timezone-aware UTC datetime `minutes` from now."""
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def _past(minutes: int = 10) -> datetime:
    """Return a timezone-aware UTC datetime `minutes` ago."""
    return datetime.now(timezone.utc) - timedelta(minutes=minutes)


def _make_token_record(
    access_token: str = "raw_access",
    refresh_token: str = "raw_refresh",
    expires_at: datetime | None = None,
    user_id: int = 1,
    strava_athlete_id: int = 999,
) -> MagicMock:
    """Build a StravaTokenORM-like MagicMock with encrypted tokens."""
    record = MagicMock()
    record.user_id = user_id
    record.strava_athlete_id = strava_athlete_id
    record.access_token = encrypt_token(access_token)
    record.refresh_token = encrypt_token(refresh_token)
    record.token_type = "Bearer"
    record.expires_in = 21600
    record.expires_at = expires_at if expires_at is not None else _future(60)
    record.scope = "activity:read_all"
    return record


# ---------------------------------------------------------------------------
# store_tokens
# ---------------------------------------------------------------------------


class TestStoreTokens:
    @pytest.mark.asyncio
    async def test_stores_encrypted_tokens(self):
        """store_tokens encrypts both tokens and calls create_or_update."""
        db = AsyncMock()
        raw_tokens = {
            "access_token": "access_abc",
            "refresh_token": "refresh_xyz",
            "token_type": "Bearer",
            "expires_in": 21600,
            "scope": "activity:read_all",
            "athlete": {"id": 42},
        }

        stored_record = MagicMock()
        stored_record.access_token = encrypt_token("access_abc")
        stored_record.refresh_token = encrypt_token("refresh_xyz")

        with patch(
            "app.services.strava_service.strava_token_repository.create_or_update",
            new_callable=AsyncMock,
            return_value=stored_record,
        ) as mock_create:
            result = await store_tokens(db, user_id=1, raw_tokens=raw_tokens)

        mock_create.assert_awaited_once()
        call_kwargs = mock_create.call_args.kwargs
        # Stored values must be ciphertext, not plaintext
        assert call_kwargs["access_token"] != "access_abc"
        assert call_kwargs["refresh_token"] != "refresh_xyz"
        assert call_kwargs["strava_athlete_id"] == 42
        # Return value has decrypted tokens set in-memory
        assert result.access_token == "access_abc"
        assert result.refresh_token == "refresh_xyz"

    @pytest.mark.asyncio
    async def test_athlete_id_extracted_from_top_level_int(self):
        """athlete_id falls back to int(athlete) when athlete is not a dict."""
        db = AsyncMock()
        raw_tokens = {
            "access_token": "a",
            "refresh_token": "r",
            "token_type": "Bearer",
            "expires_in": 100,
            "scope": "",
            "athlete": 77,
        }

        stored_record = MagicMock()
        stored_record.access_token = encrypt_token("a")
        stored_record.refresh_token = encrypt_token("r")

        with patch(
            "app.services.strava_service.strava_token_repository.create_or_update",
            new_callable=AsyncMock,
            return_value=stored_record,
        ) as mock_create:
            await store_tokens(db, user_id=1, raw_tokens=raw_tokens)

        assert mock_create.call_args.kwargs["strava_athlete_id"] == 77

    @pytest.mark.asyncio
    async def test_explicit_athlete_id_overrides_payload(self):
        """Explicitly passed athlete_id takes precedence over raw_tokens["athlete"]."""
        db = AsyncMock()
        raw_tokens = {
            "access_token": "a",
            "refresh_token": "r",
            "token_type": "Bearer",
            "expires_in": 100,
            "scope": "",
            "athlete": {"id": 1},
        }

        stored_record = MagicMock()
        stored_record.access_token = encrypt_token("a")
        stored_record.refresh_token = encrypt_token("r")

        with patch(
            "app.services.strava_service.strava_token_repository.create_or_update",
            new_callable=AsyncMock,
            return_value=stored_record,
        ) as mock_create:
            await store_tokens(db, user_id=1, raw_tokens=raw_tokens, athlete_id=999)

        assert mock_create.call_args.kwargs["strava_athlete_id"] == 999


# ---------------------------------------------------------------------------
# get_valid_token
# ---------------------------------------------------------------------------


class TestGetValidToken:
    @pytest.mark.asyncio
    async def test_returns_decrypted_token_when_valid(self):
        """get_valid_token returns ORM with decrypted access_token when not near expiry."""
        db = AsyncMock()
        record = _make_token_record(access_token="valid_access", expires_at=_future(60))

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            return_value=record,
        ):
            result = await get_valid_token(db, user_id=1)

        assert result.access_token == "valid_access"

    @pytest.mark.asyncio
    async def test_raises_when_no_token_record(self):
        """get_valid_token raises TokenRevokedError when no DB record exists."""
        db = AsyncMock()

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(TokenRevokedError):
                await get_valid_token(db, user_id=1)

    @pytest.mark.asyncio
    async def test_refreshes_when_near_expiry(self):
        """get_valid_token triggers _do_refresh when token expires within 5 minutes."""
        db = AsyncMock()
        expiring_record = _make_token_record(expires_at=_future(2))  # 2 min left
        refreshed_record = _make_token_record(access_token="fresh_access", expires_at=_future(360))

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            side_effect=[expiring_record, refreshed_record],
        ), patch(
            "app.services.strava_service._do_refresh",
            new_callable=AsyncMock,
            return_value={"access_token": "fresh_access"},
        ):
            result = await get_valid_token(db, user_id=1)

        assert result.access_token == "fresh_access"

    @pytest.mark.asyncio
    async def test_raises_when_near_expiry_and_no_refresh_token(self):
        """get_valid_token raises TokenRevokedError when near expiry but no refresh token."""
        db = AsyncMock()
        record = _make_token_record(expires_at=_future(2))
        record.refresh_token = None  # No refresh token available

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            return_value=record,
        ):
            with pytest.raises(TokenRevokedError, match="No refresh token"):
                await get_valid_token(db, user_id=1)

    @pytest.mark.asyncio
    async def test_deletes_token_and_raises_on_refresh_failure(self):
        """get_valid_token deletes the token record and raises TokenRevokedError on refresh failure."""
        db = AsyncMock()
        record = _make_token_record(expires_at=_future(2))

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            return_value=record,
        ), patch(
            "app.services.strava_service._do_refresh",
            new_callable=AsyncMock,
            side_effect=StravaRefreshError("Strava returned 401"),
        ), patch(
            "app.services.strava_service.strava_token_repository.delete_by_user_id",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_delete:
            with pytest.raises(TokenRevokedError, match="revoked"):
                await get_valid_token(db, user_id=1)

        mock_delete.assert_awaited_once_with(db, 1)

    @pytest.mark.asyncio
    async def test_raises_when_expired_token_no_expires_at(self):
        """get_valid_token treats None expires_at as needs-refresh."""
        db = AsyncMock()
        record = _make_token_record()
        record.expires_at = None  # Missing expiry → must refresh
        record.refresh_token = None  # No refresh token

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            return_value=record,
        ):
            with pytest.raises(TokenRevokedError):
                await get_valid_token(db, user_id=1)


# ---------------------------------------------------------------------------
# revoke_and_delete
# ---------------------------------------------------------------------------


class TestRevokeAndDelete:
    @pytest.mark.asyncio
    async def test_revokes_and_deletes_when_token_exists(self):
        """revoke_and_delete calls Strava revoke endpoint and deletes local record."""
        db = AsyncMock()
        record = _make_token_record(access_token="access_to_revoke")

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            return_value=record,
        ), patch(
            "app.services.strava_service.strava_token_repository.delete_by_user_id",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_delete, patch(
            "app.services.strava_service.httpx.AsyncClient"
        ) as mock_client_cls:
            mock_http = AsyncMock()
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_http

            result = await revoke_and_delete(db, user_id=1)

        assert result is True
        mock_delete.assert_awaited_once_with(db, 1)
        mock_http.post.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_false_when_no_token_exists(self):
        """revoke_and_delete returns False when no token record found."""
        db = AsyncMock()

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            return_value=None,
        ), patch(
            "app.services.strava_service.strava_token_repository.delete_by_user_id",
            new_callable=AsyncMock,
            return_value=False,
        ):
            result = await revoke_and_delete(db, user_id=1)

        assert result is False

    @pytest.mark.asyncio
    async def test_still_deletes_locally_when_strava_revoke_fails(self):
        """revoke_and_delete deletes local record even if Strava revoke call raises."""
        db = AsyncMock()
        record = _make_token_record(access_token="access")

        with patch(
            "app.services.strava_service.strava_token_repository.get_by_user_id",
            new_callable=AsyncMock,
            return_value=record,
        ), patch(
            "app.services.strava_service.strava_token_repository.delete_by_user_id",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_delete, patch(
            "app.services.strava_service.httpx.AsyncClient"
        ) as mock_client_cls:
            mock_http = AsyncMock()
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_http.post = AsyncMock(side_effect=Exception("network error"))
            mock_client_cls.return_value = mock_http

            result = await revoke_and_delete(db, user_id=1)

        assert result is True
        mock_delete.assert_awaited_once_with(db, 1)
