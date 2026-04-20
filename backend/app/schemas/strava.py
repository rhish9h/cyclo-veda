"""Pydantic schemas for Strava API responses.

Defines normalized response models so the frontend receives a stable,
documented contract rather than raw Strava payload shapes.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StravaActivity(BaseModel):
    """Normalized representation of a single Strava activity.

    Maps a subset of Strava's SummaryActivity payload to a stable schema.
    Only fields needed for Cyclo Veda v1 are included; the rest are discarded
    at the service boundary to keep responses lean.
    """

    id: int = Field(description="Strava activity ID")
    name: str = Field(description="Activity name")
    sport_type: str = Field(description="Sport type, e.g. 'Ride', 'Run'")
    start_date: datetime = Field(description="Activity start time (UTC)")
    distance_meters: float = Field(description="Total distance in metres")
    moving_time_seconds: int = Field(description="Moving time in seconds")
    elapsed_time_seconds: int = Field(description="Elapsed time in seconds")
    total_elevation_gain_meters: float = Field(description="Elevation gain in metres")
    average_speed_mps: Optional[float] = Field(None, description="Average speed in m/s")
    max_speed_mps: Optional[float] = Field(None, description="Max speed in m/s")
    average_heartrate: Optional[float] = Field(None, description="Average heart rate (bpm)")
    max_heartrate: Optional[float] = Field(None, description="Max heart rate (bpm)")
    average_watts: Optional[float] = Field(None, description="Average power output (watts)")
    kilojoules: Optional[float] = Field(None, description="Total energy output (kJ)")
    kudos_count: int = Field(0, description="Number of kudos received")
    achievement_count: int = Field(0, description="Number of achievements")
    athlete_count: int = Field(1, description="Number of athletes in the activity")
    map_summary_polyline: Optional[str] = Field(None, description="Encoded polyline for activity route")

    @classmethod
    def from_strava(cls, raw: dict) -> "StravaActivity":
        """Construct a normalized StravaActivity from a raw Strava API payload.

        Args:
            raw: Single activity dict as returned by GET /athlete/activities

        Returns:
            Normalized StravaActivity instance
        """
        map_data = raw.get("map") or {}
        return cls(
            id=raw["id"],
            name=raw.get("name", ""),
            sport_type=raw.get("sport_type") or raw.get("type", ""),
            start_date=raw["start_date"],
            distance_meters=raw.get("distance", 0.0),
            moving_time_seconds=raw.get("moving_time", 0),
            elapsed_time_seconds=raw.get("elapsed_time", 0),
            total_elevation_gain_meters=raw.get("total_elevation_gain", 0.0),
            average_speed_mps=raw.get("average_speed"),
            max_speed_mps=raw.get("max_speed"),
            average_heartrate=raw.get("average_heartrate"),
            max_heartrate=raw.get("max_heartrate"),
            average_watts=raw.get("average_watts"),
            kilojoules=raw.get("kilojoules"),
            kudos_count=raw.get("kudos_count", 0),
            achievement_count=raw.get("achievement_count", 0),
            athlete_count=raw.get("athlete_count", 1),
            map_summary_polyline=map_data.get("summary_polyline"),
        )


class StravaActivitiesResponse(BaseModel):
    """Paginated response for /api/strava/activities."""

    activities: List[StravaActivity]
    page: int
    per_page: int
    count: int = Field(description="Number of activities returned in this page")


class StravaStatus(BaseModel):
    """Response schema for /api/strava/status."""

    connected: bool
    athlete_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_expiring_soon: bool = False
    has_refresh_token: bool = False
    scope: Optional[str] = None
