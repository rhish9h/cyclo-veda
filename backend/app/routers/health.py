"""Health check router module for Cyclo Veda.

This module defines health check endpoints for monitoring and service discovery:
- Root endpoint with welcome message
- Dedicated health check endpoint for Docker and monitoring systems
"""

from datetime import datetime
from fastapi import APIRouter

# Constants - should match main.py constants
API_VERSION = "0.1.0"
API_TITLE = "Cyclo Veda API"

# Router configuration
router = APIRouter(
    tags=["Health"],
)


@router.get("/")
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": f"Welcome to {API_TITLE}",
        "status": "healthy",
        "version": API_VERSION,
    }


@router.get("/health")
async def health_check():
    """Dedicated health check endpoint for monitoring and Docker health checks."""
    return {
        "status": "healthy",
        "service": "cyclo-veda-backend",
        "version": API_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
