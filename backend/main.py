"""Bangladesh Crop Intelligence Assistant - FastAPI Backend API.

Main application entrypoint configuring middleware, routes, and exception handlers.
"""

import os
import sys
from pathlib import Path

# Ensure project root and backend directory are in sys.path
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
for p in (str(ROOT_DIR), str(BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.crops import router as crops_router
from routes.assistant import router as assistant_router

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Bangladesh Crop Intelligence API",
    description="RESTful API providing crop intelligence, growth stages, diseases, and region mapping for Bangladesh agriculture.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS origins
raw_cors = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,*")
cors_origins = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(crops_router)
app.include_router(assistant_router)


@app.get("/", tags=["Health"])
def health_check():
    """Root health check endpoint."""
    return {
        "status": "online",
        "service": "Bangladesh Crop Intelligence API",
        "version": "2.0.0",
        "documentation": "/docs",
    }
