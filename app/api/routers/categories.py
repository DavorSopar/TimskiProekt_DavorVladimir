"""Category endpoints (API_CONTRACT.md §3).

Endpoints are implemented in SCRUM-09.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/categories", tags=["categories"])
