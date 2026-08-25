"""Aggregates all resource routers under a single ``/api`` router.

Each resource (transactions, categories, budgets, CSV import, analytics)
owns its own router module; endpoints are added to them per issue.
"""

from fastapi import APIRouter

from app.api.routers import analytics, budgets, categories, csv_import, transactions

api_router = APIRouter()
api_router.include_router(transactions.router)
api_router.include_router(categories.router)
api_router.include_router(budgets.router)
api_router.include_router(csv_import.router)
api_router.include_router(analytics.router)

__all__ = ["api_router"]
