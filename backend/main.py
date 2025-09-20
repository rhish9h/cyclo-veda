"""Main FastAPI application entry point for Cyclo Veda.

This module sets up the FastAPI application with middleware, CORS configuration,
and includes all API routers.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import routers
from app.routers import auth, health

# Load environment variables
load_dotenv()

# Constants
API_VERSION = "0.1.0"
API_TITLE = "Cyclo Veda API"
API_DESCRIPTION = "Backend API for Cyclo Veda Application"

# Development CORS origins
DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    # Docker hostnames
    "http://cycloveda.local",
    "https://cycloveda.local",
]


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

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=DEV_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(health.router)  # Health endpoints at root level
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
