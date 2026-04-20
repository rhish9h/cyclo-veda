"""
Strava integration router

Handles OAuth flow initiation, callback, status, disconnect, and activity retrieval.
"""

import hmac
import hashlib
import os
import time
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.schemas.user import User
from app.services.strava_service import (
    check_token_status,
    get_user_tokens,
    refresh_access_token,
    revoke_and_delete,
    store_tokens,
)

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# HMAC key for state signing — server-side only, never exposed to the client
_STATE_HMAC_KEY = os.getenv("STRAVA_STATE_SALT", "cyclo-veda-default-salt")

router = APIRouter(prefix="/strava", tags=["strava"])

# --------------------------------------------------------------------------- #
#  State signing  (prevents CSRF / user-mismatch on callback)               #
# --------------------------------------------------------------------------- #


def _sign_state(user_id: int) -> str:
    """Create a signed state string: HMAC-SHA256(user_id:timestamp).

    The HMAC key is server-side only — never embedded in the state payload.
    """
    ts = str(int(time.time()))
    payload = f"{user_id}:{ts}"
    sig = hmac.new(_STATE_HMAC_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def _verify_state(raw_state: str) -> Optional[int]:
    """Return user_id if the state is valid and not older than 10 minutes, else None."""
    if not raw_state or ":" not in raw_state:
        return None
    parts = raw_state.rsplit(":", 1)
    if len(parts) != 2:
        return None
    payload, sig = parts
    payload_parts = payload.split(":")
    if len(payload_parts) != 2:
        return None
    user_id_str, ts_str = payload_parts
    expected = hmac.new(_STATE_HMAC_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return None
    # Reject states older than 10 minutes
    if int(ts_str) < int(time.time()) - 600:
        return None
    return int(user_id_str)


# --------------------------------------------------------------------------- #
#  Helpers (must be defined before routes that use them via Depends)         #
# --------------------------------------------------------------------------- #


async def _extract_bearer_token(request: Request) -> str:
    """Extract and validate a Strava bearer token from the Authorization header."""
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="No Authorization header")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = parts[1]
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")

    return token


async def _exchange_code_for_tokens(code: str) -> dict[str, Any]:
    """Exchange an authorization code for Strava access tokens."""
    token_url = "https://www.strava.com/oauth/token"
    data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(token_url, data=data)

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Strava token exchange failed: {response.status_code} - {response.text}",
        )

    tokens: dict[str, Any] = response.json()
    if "access_token" not in tokens:
        raise HTTPException(status_code=502, detail="Strava response missing access_token")

    return tokens


# Alias for Depends() syntax (must be defined before routes)
get_user_bearer_token = _extract_bearer_token


# --------------------------------------------------------------------------- #
#  Routes                                                                     #
# --------------------------------------------------------------------------- #


@router.get("/connect")
async def connect_strava(user: User = Depends(get_current_user)):
    """Generate the Strava OAuth authorization link for the authenticated user.

    Embeds a signed state parameter carrying user_id so the callback can
    identify the user without a JWT (the browser callback has no auth header).
    """
    signed_state = _sign_state(user.id)
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}&"
        f"redirect_uri={STRAVA_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=activity:read_all&"
        f"state={signed_state}&"
        f"approval_prompt=auto"
    )
    return {"auth_url": auth_url}


@router.get("/callback")
async def strava_callback(
    request: Request,
    state: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Handle OAuth callback from Strava.

    Identifies the user via the signed state parameter (set in /connect).
    This avoids relying on JWT auth which the browser callback cannot provide.
    """
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?error=strava_auth_failed",
            status_code=302,
        )

    if not code:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?error=strava_no_code",
            status_code=302,
        )

    # Verify signed state to identify the user
    user_id = _verify_state(state) if state else None
    if user_id is None:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?error=strava_invalid_state",
            status_code=302,
        )

    # Exchange code for tokens
    try:
        tokens = await _exchange_code_for_tokens(code)
    except HTTPException:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?error=strava_token_exchange_failed",
            status_code=302,
        )

    # Extract athlete_id from Strava response
    athlete = tokens.get("athlete")
    athlete_id = None
    if isinstance(athlete, dict):
        athlete_id = athlete.get("id")
    elif athlete is not None:
        athlete_id = int(athlete)

    # Store tokens with athlete_id
    await store_tokens(db, user_id, tokens, athlete_id=athlete_id)
    return RedirectResponse(
        url=f"{FRONTEND_URL}/settings?strava_connected=true",
        status_code=302,
    )


@router.get("/status")
async def get_strava_status(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Check connection status and token expiry for the authenticated user."""
    status = await check_token_status(db, user.id)
    return JSONResponse(content=status)


@router.delete("/disconnect")
async def disconnect_strava(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Revoke Strava token and remove stored credentials."""
    deleted = await revoke_and_delete(db, user.id)
    if deleted:
        return JSONResponse(content={"message": "Strava account disconnected", "deleted": True})
    return JSONResponse(content={"message": "No Strava account linked", "deleted": False}, status_code=404)


@router.get("/token")
async def get_current_tokens(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Return decrypted Strava tokens for frontend use (e.g., fetching activities)."""
    tokens = await get_user_tokens(db, user.id)
    if tokens is None:
        return JSONResponse(content={"error": "No tokens found"}, status_code=404)
    return tokens


@router.post("/refresh")
async def refresh_strava_token(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Attempt to refresh an expired Strava access token."""
    result = await refresh_access_token(db, user.id)
    if result:
        return {"message": "Token refreshed successfully", "data": result}
    return JSONResponse(content={"error": "Token refresh failed or no refresh token available"}, status_code=400)


@router.get("/user")
async def get_current_strava_user(token: str = Depends(get_user_bearer_token)):
    """Fetch the current Strava user profile using a bearer token."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            "https://www.strava.com/api/v3/athlete",
            headers={"Authorization": f"Bearer {token}"},
        )

    if resp.status_code != 200:
        return JSONResponse(content={"error": "Failed to fetch Strava user profile"}, status_code=resp.status_code)
    return resp.json()


@router.get("/activities")
async def get_current_strava_activities(
    auth_token: str = Depends(get_user_bearer_token),
    before: Optional[int] = Query(None, description="Only return activities created before this Unix timestamp"),
    after: Optional[int] = Query(None, description="Only return activities created after this Unix timestamp"),
    limit: int = Query(30, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    """Fetch Strava activities."""
    params: dict[str, Any] = {"per_page": limit, "page": page}
    if before:
        params["before"] = before
    if after:
        params["after"] = after

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {auth_token}"},
            params=params,
        )

    if resp.status_code != 200:
        return JSONResponse(content={"error": "Failed to fetch activities"}, status_code=resp.status_code)
    return resp.json()
