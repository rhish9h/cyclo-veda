"""Strava OAuth service layer.

Handles token refresh, storage, and status checks using the repository
and encryption utilities.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Literal, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strava_token import StravaTokenORM
from app.repositories.strava_token_repository import strava_token_repository
from app.utils.security import decrypt_token, encrypt_token


STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"


class StravaServiceError(Exception):
    """Base exception for Strava service operations."""
    pass


def generate_strava_auth_url() -> str:
    """Generate the Strava OAuth authorization URL.

    Returns:
        Full authorization URL string ready for frontend redirect
    """
    scope = "activity:read_all"
    redirect_uri = os.getenv("STRAVA_REDIRECT_URI", "http://localhost/api/strava/callback")
    return (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&approval_prompt=force"
    )


async def store_tokens(
    db: AsyncSession,
    user_id: int,
    raw_tokens: Dict[str, str | int],
    athlete_id: Optional[int] = None,
) -> Optional[StravaTokenORM]:
    """Encrypt and store Strava OAuth tokens for a user.

    Args:
        db: Async database session
        user_id: User primary key
        raw_tokens: Dict from Strava OAuth token response
                    (must contain access_token, refresh_token, token_type, expires_in)
        athlete_id: Strava athlete ID (extracted from raw_tokens["athlete"]["id"]
                    or the top-level "athlete" key)

    Returns:
        Stored StravaTokenORM record or None on failure
    """
    access_token = str(raw_tokens.get("access_token", ""))
    refresh_token = str(raw_tokens.get("refresh_token", ""))
    token_type = str(raw_tokens.get("token_type", "Bearer"))
    expires_in = int(raw_tokens.get("expires_in", 0))
    scope = str(raw_tokens.get("scope", ""))

    # Extract athlete_id from Strava response (can be nested or top-level)
    if athlete_id is None:
        athlete = raw_tokens.get("athlete")
        if isinstance(athlete, dict):
            athlete_id = athlete.get("id")
        elif athlete is not None:
            athlete_id = int(athlete)

    # Calculate absolute expiry in UTC
    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(seconds=expires_in) if expires_in else now_utc

    # Encrypt tokens before persistence
    encrypted_access = encrypt_token(access_token)
    encrypted_refresh = encrypt_token(refresh_token) if refresh_token else None

    record = await strava_token_repository.create_or_update(
        db=db,
        user_id=user_id,
        access_token=encrypted_access,
        refresh_token=encrypted_refresh,
        token_type=token_type,
        expires_in=expires_in,
        expires_at=expires_at,
        scope=scope,
        strava_athlete_id=athlete_id,
    )

    # Decrypt for return value
    record.access_token = access_token
    record.refresh_token = refresh_token
    return record


async def get_user_tokens(db: AsyncSession, user_id: int) -> Optional[Dict[str, str | int | None]]:
    """Retrieve and decrypt Strava tokens for a user.

    Args:
        db: Async database session
        user_id: User primary key

    Returns:
        Dict containing decrypted tokens and metadata, or None if not found
    """
    record = await strava_token_repository.get_by_user_id(db, user_id)
    if not record or not record.access_token:
        return None

    decrypted_access = decrypt_token(record.access_token)
    decrypted_refresh = decrypt_token(record.refresh_token) if record.refresh_token else None

    return {
        "access_token": decrypted_access,
        "refresh_token": decrypted_refresh,
        "token_type": record.token_type,
        "expires_in": record.expires_in,
        "expires_at": record.expires_at.isoformat() if record.expires_at else None,
        "scope": record.scope,
    }


async def check_token_status(db: AsyncSession, user_id: int) -> Dict:
    """Check whether a user's tokens exist and are valid.

    Args:
        db: Async database session
        user_id: User primary key

    Returns:
        Dict with connection status and expiry info
    """
    record = await strava_token_repository.get_by_user_id(db, user_id)
    if not record or not record.access_token:
        return {"connected": False, "expires_at": None, "error": "No token record"}

    expires_at = record.expires_at
    now_utc = datetime.now(timezone.utc)
    has_refresh = bool(record.refresh_token)

    # Define safety window: consider token "expiring soon" if < 5 minutes left
    safety_window = timedelta(minutes=5)
    is_expiring_soon = expires_at and (expires_at - now_utc) < safety_window

    # Try to decrypt to verify key validity
    try:
        decrypt_token(record.access_token)
        key_valid = True
    except ValueError:
        key_valid = False

    return {
        "connected": True,
        "token_type": record.token_type,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "expires_in": record.expires_in,
        "is_expiring_soon": is_expiring_soon,
        "has_refresh_token": has_refresh,
        "key_valid": key_valid,
    }


async def refresh_access_token(db: AsyncSession, user_id: int) -> Optional[Dict]:
    """Attempt to refresh Strava access token using stored refresh token.

    Returns updated token payload on success, None on failure.
    """
    from httpx import AsyncClient, Timeout

    record = await strava_token_repository.get_by_user_id(db, user_id)
    if not record or not record.refresh_token:
        return None

    try:
        decrypted_refresh = decrypt_token(record.refresh_token)
    except ValueError:
        return None

    async with AsyncClient(timeout=Timeout(10.0)) as client:
        resp = await client.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id": STRAVA_CLIENT_ID,
                "client_secret": STRAVA_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": decrypted_refresh,
            },
        )

    if resp.status_code != 200:
        return None

    new_tokens = resp.json()
    # Store refreshed tokens
    await store_tokens(db, user_id, new_tokens)
    return new_tokens


async def revoke_and_delete(db: AsyncSession, user_id: int) -> bool:
    """Revoke token with Strava and delete local record.

    Args:
        db: Async database session
        user_id: User primary key

    Returns:
        True if local record was deleted (Strava revocation is best-effort)
    """
    from httpx import AsyncClient, Timeout

    record = await strava_token_repository.get_by_user_id(db, user_id)
    if not record or not record.refresh_token:
        pass  # Best-effort revocation below

    # Best-effort revoke with Strava (using access token)
    try:
        decrypted_access = decrypt_token(record.access_token) if record else None
        if decrypted_access:
            async with AsyncClient(timeout=Timeout(10.0)) as client:
                await client.post(
                    "https://www.strava.com/oauth/revoke",
                    params={"access_token": decrypted_access},
                )
    except Exception:
        pass  # Ignore revocation failures; we still delete locally

    deleted = await strava_token_repository.delete_by_user_id(db, user_id)
    return deleted
