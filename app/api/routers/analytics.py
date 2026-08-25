"""Analytics endpoints (API_CONTRACT.md §6).

Endpoints are implemented in SCRUM-15.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["analytics"])
