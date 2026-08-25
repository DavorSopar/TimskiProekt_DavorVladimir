"""FastAPI application entry point.

Run locally with:

    uv run uvicorn app.main:app --reload

Serves at http://127.0.0.1:8000 with all resource endpoints under /api,
per API_CONTRACT.md §1.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import api_router
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the local SQLite database/tables if they don't exist yet."""
    init_db()
    yield


app = FastAPI(title="Personal Finance Tracker API", lifespan=lifespan)
app.include_router(api_router, prefix="/api")
