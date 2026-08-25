"""Budget endpoints (API_CONTRACT.md §4)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import BudgetCreate, BudgetRead, BudgetStatus, BudgetUpdate
from app.database import get_db
from app.services import budgets as budgets_service
from app.services.budgets import BudgetAlreadyExists

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetRead, status_code=201)
def create_budget(data: BudgetCreate, db: Session = Depends(get_db)):
    try:
        return budgets_service.create_budget(db, data.category, data.month, data.amount_cents)
    except BudgetAlreadyExists:
        raise HTTPException(
            status_code=409, detail="A budget for this category and month already exists"
        )


@router.get("", response_model=list[BudgetRead])
def list_budgets(month: str | None = None, db: Session = Depends(get_db)):
    return budgets_service.list_budgets(db, month=month)


@router.put("/{budget_id}", response_model=BudgetRead)
def update_budget(budget_id: int, data: BudgetUpdate, db: Session = Depends(get_db)):
    budget = budgets_service.update_budget_amount(db, budget_id, data.amount_cents)
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.get("/{budget_id}/status", response_model=BudgetStatus)
def get_budget_status(budget_id: int, db: Session = Depends(get_db)):
    budget = budgets_service.get_budget(db, budget_id)
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budgets_service.get_budget_status(db, budget)
