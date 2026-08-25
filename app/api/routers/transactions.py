"""Transaction endpoints (API_CONTRACT.md §2).

Endpoints are implemented in SCRUM-07.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/transactions", tags=["transactions"])
