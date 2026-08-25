"""CSV import endpoint (API_CONTRACT.md §5).

Endpoint is implemented in SCRUM-13.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/import", tags=["import"])
