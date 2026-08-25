"""Centralized HTTP client for the FastAPI backend.

Every Streamlit page should call the backend through this module rather
than issuing its own `requests` calls, so error handling and the base
URL stay in one place. See API_CONTRACT.md for the full endpoint
contract this client is built against.
"""

from __future__ import annotations

import os

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
_TIMEOUT_SECONDS = 5


class APIError(Exception):
    """Raised when the backend is unreachable or returns an error response."""


def get_base_url() -> str:
    """Return the backend base URL from FINANCE_API_URL, or the local default."""
    return os.environ.get("FINANCE_API_URL", DEFAULT_BASE_URL)


def get_categories() -> list[dict]:
    """Call GET /api/categories and return the parsed JSON list.

    This is the first real call wired up for SCRUM-06 — it also doubles
    as a lightweight backend-connectivity check on app startup, since
    categories are always seeded on a fresh database (API_CONTRACT.md §3).
    """
    url = f"{get_base_url()}/api/categories"
    try:
        response = requests.get(url, timeout=_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise APIError(f"Could not reach backend at {url}: {exc}") from exc

    if not response.ok:
        raise APIError(f"Backend returned {response.status_code} for {url}")

    return response.json()
