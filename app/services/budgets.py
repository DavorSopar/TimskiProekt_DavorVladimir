"""Budget business logic and data access (API_CONTRACT.md §4)."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Budget, Transaction


class BudgetAlreadyExists(Exception):
    """Raised when a category+month combination already has a budget."""


def list_budgets(db: Session, month: str | None = None) -> list[Budget]:
    query = db.query(Budget)
    if month is not None:
        query = query.filter(Budget.month == month)
    return query.order_by(Budget.month, Budget.category).all()


def create_budget(db: Session, category: str, month: str, amount_cents: int) -> Budget:
    existing = (
        db.query(Budget)
        .filter(Budget.category == category, Budget.month == month)
        .first()
    )
    if existing is not None:
        raise BudgetAlreadyExists(f"{category} / {month}")
    budget = Budget(category=category, month=month, amount_cents=amount_cents)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def get_budget(db: Session, budget_id: int) -> Budget | None:
    return db.get(Budget, budget_id)


def update_budget_amount(db: Session, budget_id: int, amount_cents: int) -> Budget | None:
    budget = db.get(Budget, budget_id)
    if budget is None:
        return None
    budget.amount_cents = amount_cents
    db.commit()
    db.refresh(budget)
    return budget


def compute_spent_cents(db: Session, category: str, month: str) -> int:
    """Sum expense transactions in this category during this YYYY-MM month."""
    total = (
        db.query(func.coalesce(func.sum(Transaction.amount_cents), 0))
        .filter(
            Transaction.category == category,
            Transaction.type == "expense",
            func.strftime("%Y-%m", Transaction.date) == month,
        )
        .scalar()
    )
    return int(total)


def get_budget_status(db: Session, budget: Budget) -> dict:
    spent_cents = compute_spent_cents(db, budget.category, budget.month)
    remaining_cents = budget.amount_cents - spent_cents
    return {
        "budget": budget,
        "spent_cents": spent_cents,
        "remaining_cents": remaining_cents,
        "over_budget": spent_cents > budget.amount_cents,
    }
