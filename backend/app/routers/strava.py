"""
Strava integration router

Handles OAuth flow and Strava API integration
"""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/strava")

@router.get("/connect")
async def connect_strava():
    """
    Generate the strava url for OAuth flow

    Returns the URL the frontend should redirect the user to
    for Strava authentication
    """

    auth_url = (
        "https://www.strava.com/oauth/authorize?"
        "client_id=113526&"
        "redirect_uri=http://api.cycloveda.local/api/strava/callback&"
        "response_type=code&"
        "scope=activity:read_all&"
        "approval_prompt=force"
    )

    return RedirectResponse(
        url=auth_url,
        status_code=302
    )