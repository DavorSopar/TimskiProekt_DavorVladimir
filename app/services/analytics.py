"""Analytics business logic and data access (API_CONTRACT.md §6).

All analytics are computed here from persisted transactions — the UI
never re-derives totals from a raw transaction list.
"""

from datetime import date as date_type

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Transaction


def _sum_amount_cents(
    db: Session,
    transaction_type: str,
    start_date: date_type | None = None,
    end_date: date_type | None = None,
) -> int:
    query = db.query(func.coalesce(func.sum(Transaction.amount_cents), 0)).filter(
        Transaction.type == transaction_type
    )
    if start_date is not None:
        query = query.filter(Transaction.date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.date <= end_date)
    return int(query.scalar())


def get_summary(
    db: Session, start_date: date_type | None = None, end_date: date_type | None = None
) -> dict:
    total_income_cents = _sum_amount_cents(db, "income", start_date, end_date)
    total_expenses_cents = _sum_amount_cents(db, "expense", start_date, end_date)
    return {
        "total_income_cents": total_income_cents,
        "total_expenses_cents": total_expenses_cents,
        "net_balance_cents": total_income_cents - total_expenses_cents,
    }


def get_by_category(
    db: Session, start_date: date_type | None = None, end_date: date_type | None = None
) -> list[dict]:
    query = db.query(
        Transaction.category, func.sum(Transaction.amount_cents).label("total_cents")
    ).filter(Transaction.type == "expense")
    if start_date is not None:
        query = query.filter(Transaction.date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.date <= end_date)
    rows = query.group_by(Transaction.category).order_by(
        func.sum(Transaction.amount_cents).desc()
    ).all()
    return [{"category": category, "total_cents": int(total_cents)} for category, total_cents in rows]


def _last_n_months(n: int, today: date_type | None = None) -> list[str]:
    """The last ``n`` YYYY-MM labels ending with the current month, oldest first."""
    today = today or date_type.today()
    year, month = today.year, today.month
    months = []
    for _ in range(n):
        months.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return list(reversed(months))


def get_monthly_trend(db: Session, months: int = 6) -> list[dict]:
    month_labels = _last_n_months(months)

    income_by_month = dict(
        db.query(func.strftime("%Y-%m", Transaction.date), func.sum(Transaction.amount_cents))
        .filter(Transaction.type == "income")
        .group_by(func.strftime("%Y-%m", Transaction.date))
        .all()
    )
    expenses_by_month = dict(
        db.query(func.strftime("%Y-%m", Transaction.date), func.sum(Transaction.amount_cents))
        .filter(Transaction.type == "expense")
        .group_by(func.strftime("%Y-%m", Transaction.date))
        .all()
    )

    return [
        {
            "month": month,
            "income_cents": int(income_by_month.get(month, 0)),
            "expenses_cents": int(expenses_by_month.get(month, 0)),
        }
        for month in month_labels
    ]
