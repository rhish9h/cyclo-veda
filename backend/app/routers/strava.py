"""
Strava integration router

Handles OAuth flow and Strava API integration
"""

import os
import httpx
from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from typing import Optional, Dict, Any

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")

router = APIRouter(prefix="/strava")

@router.get("/connect")
async def connect_strava():
    """
    Generate the strava url for OAuth flow

    Returns the URL the frontend should redirect the user to
    for Strava authentication
    """

    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}&"
        f"redirect_uri={STRAVA_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=activity:read_all&"
        f"approval_prompt=force"
    )

    return RedirectResponse(
        url=auth_url,
        status_code=302
    )

@router.get("/callback")
async def strava_callback(
    request: Request,
    state: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """
    Handles OAuth callback from Strava

    Strava redirects here after user authorization.
    We exchange the code for tokens and redirect back to frontend.
    """
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?error=strava_auth_failed",
            status_code=302
        )
    
    if not code:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?error=strava_no_code",
            status_code=302
        )

    try:
        # Exchange authorization code for token
        tokens = await exchange_code_for_tokens(code)
        print(tokens) # TODO remove this - added for debugging

        # TODO Implement token storage

        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?strava_connected=true",
            status_code=302
        )

    except Exception as exc:
        # Log error for debugging
        print(f"Strava token exchange failed: {str(exc)}")

        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?error=strava_token_exchange_failed",
            status_code=302
        )

async def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    """
    Exchange authorization code for Strava access tokens

    Args:
        code: The authorization code received from Strava callback

    Returns:
        Dict containing the token responses from Strava

    Raises:
        Exception: If token exchange fails
    """
    token_url = "https://www.strava.com/oauth/token"

    data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)

        if response.status_code != 200:
            error_detail = response.text
            raise Exception(f"Strava token exchange failed: {response.status_code} - {error_detail}")

        tokens = response.json()

        # Validate required fields
        if "access_token" not in tokens:
            raise Exception("Strava response missing access_token")

        return tokens