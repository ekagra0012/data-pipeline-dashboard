"""
backend/main.py — FastAPI Application Entry Point

Run with:
    uvicorn backend.main:app --reload --port 8000
"""

import sys
import pathlib

# Ensure project root is on sys.path when running from any directory
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routers.data import router
from backend.config import FRONTEND_DIR

app = FastAPI(
    title="Data Analytics Dashboard API",
    description="REST API for the data pipeline analytics dashboard.",
    version="1.0.0",
)

# F-27: CORS — allow all origins for GET requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}


# Data routes
app.include_router(router, tags=["data"])

# Serve the built React frontend as static files (fallback)
# This makes everything accessible from port 8000 too.
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
