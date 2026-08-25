"""Budget endpoints (API_CONTRACT.md §4).

Endpoints are implemented in SCRUM-11.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/budgets", tags=["budgets"])
