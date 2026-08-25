"""Centralized HTTP client for the FastAPI backend.

Every Streamlit page should call the backend through this module rather
than issuing its own `requests` calls, so error handling and the base
URL stay in one place. See API_CONTRACT.md for the full endpoint
contract this client is built against.
"""

from __future__ import annotations

import os
from typing import Any

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
_TIMEOUT_SECONDS = 5


class APIError(Exception):
    """Raised when the backend is unreachable or returns an error response."""


def get_base_url() -> str:
    """Return the backend base URL from FINANCE_API_URL, or the local default."""
    return os.environ.get("FINANCE_API_URL", DEFAULT_BASE_URL)


def _extract_error_detail(response: requests.Response) -> str:
    """Pull a human-readable message out of an error response.

    Handles both error shapes documented in API_CONTRACT.md §7: a plain
    `{"detail": "message"}` and FastAPI's default 422 validation shape
    `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`.
    """
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip() or f"HTTP {response.status_code}"

    detail = payload.get("detail") if isinstance(payload, dict) else None
    if detail is None:
        return f"HTTP {response.status_code}"
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        first = detail[0]
        if isinstance(first, dict):
            loc = first.get("loc") or []
            field = loc[-1] if loc else None
            msg = first.get("msg", str(first))
            return f"{field}: {msg}" if field else msg
        return str(first)
    return str(detail)


def _request(method: str, path: str, **kwargs: Any) -> requests.Response:
    """Send one HTTP request to the backend and raise APIError on any failure."""
    url = f"{get_base_url()}{path}"
    try:
        response = requests.request(method, url, timeout=_TIMEOUT_SECONDS, **kwargs)
    except requests.RequestException as exc:
        raise APIError(f"Could not reach backend at {url}: {exc}") from exc

    if not response.ok:
        raise APIError(_extract_error_detail(response))

    return response


def get_categories() -> list[dict]:
    """GET /api/categories — also doubles as the app's connectivity check."""
    return _request("GET", "/api/categories").json()


def list_transactions(
    *,
    category: str | None = None,
    type_: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict]:
    """GET /api/transactions, with optional filters (combine with AND)."""
    params = {
        "category": category,
        "type": type_,
        "start_date": start_date,
        "end_date": end_date,
    }
    params = {key: value for key, value in params.items() if value}
    return _request("GET", "/api/transactions", params=params).json()


def create_transaction(
    *, date: str, description: str, category: str, amount_cents: int, type_: str
) -> dict:
    """POST /api/transactions."""
    body = {
        "date": date,
        "description": description,
        "category": category,
        "amount_cents": amount_cents,
        "type": type_,
    }
    return _request("POST", "/api/transactions", json=body).json()


def update_transaction(
    transaction_id: int,
    *,
    date: str,
    description: str,
    category: str,
    amount_cents: int,
    type_: str,
) -> dict:
    """PUT /api/transactions/{id} — full replace, not a partial patch."""
    body = {
        "date": date,
        "description": description,
        "category": category,
        "amount_cents": amount_cents,
        "type": type_,
    }
    return _request("PUT", f"/api/transactions/{transaction_id}", json=body).json()


def delete_transaction(transaction_id: int) -> None:
    """DELETE /api/transactions/{id}."""
    _request("DELETE", f"/api/transactions/{transaction_id}")


def list_budgets(*, month: str | None = None) -> list[dict]:
    """GET /api/budgets, optionally filtered by month (YYYY-MM)."""
    params = {"month": month} if month else {}
    return _request("GET", "/api/budgets", params=params).json()


def create_budget(*, category: str, month: str, amount_cents: int) -> dict:
    """POST /api/budgets. Raises APIError (409) if one already exists — use update_budget."""
    body = {"category": category, "month": month, "amount_cents": amount_cents}
    return _request("POST", "/api/budgets", json=body).json()


def update_budget(budget_id: int, *, amount_cents: int) -> dict:
    """PUT /api/budgets/{id}."""
    return _request("PUT", f"/api/budgets/{budget_id}", json={"amount_cents": amount_cents}).json()


def get_budget_status(budget_id: int) -> dict:
    """GET /api/budgets/{id}/status -> {budget, spent_cents, remaining_cents, over_budget}."""
    return _request("GET", f"/api/budgets/{budget_id}/status").json()
