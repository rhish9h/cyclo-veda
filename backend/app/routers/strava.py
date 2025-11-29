"""
Strava integration router

Handles OAuth flow and Strava API integration
"""

import os
from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from typing import Optional

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")

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
            url="http://localhost:5173/settings?error=strava_auth_failed", # TODO: keep urls in a central location
            status_code=302
        )
    
    if not code:
        return RedirectResponse(
            url="http://localhost:5173/settings?error=strava_no_code",
            status_code=302
        )

    return RedirectResponse(
        url="http://localhost:5173/settings",
        status_code=302
    )