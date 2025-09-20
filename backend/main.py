"""Main FastAPI application entry point for Cyclo Veda.

This module sets up the FastAPI application and includes all API routers.
CORS is handled at the Traefik reverse proxy level.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

# Import routers
from app.routers import auth, health

# Load environment variables
load_dotenv()

# Constants
API_VERSION = "0.1.0"
API_TITLE = "Cyclo Veda API"
API_DESCRIPTION = "Backend API for Cyclo Veda Application"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup: Initialize resources
    print(f"🚀 Starting {API_TITLE} v{API_VERSION}...")
    yield
    # Shutdown: Clean up resources
    print("🛑 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

# Include routers
app.include_router(health.router)  # Health endpoints at root level
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
