"""SQLAlchemy ORM models.

Shapes must match API_CONTRACT.md exactly — do not add or rename fields
here without updating that document in the same change.
"""

from datetime import date as date_type
from datetime import datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Transaction(Base):
    """A single income or expense entry (API_CONTRACT.md §2)."""

    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name="ck_transactions_amount_cents_positive"),
        CheckConstraint("type IN ('income', 'expense')", name="ck_transactions_type_valid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(7), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return (
            f"Transaction(id={self.id!r}, date={self.date!r}, type={self.type!r}, "
            f"amount_cents={self.amount_cents!r}, category={self.category!r})"
        )


class Category(Base):
    """A user-manageable transaction category (API_CONTRACT.md §3)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"Category(id={self.id!r}, name={self.name!r})"


class Budget(Base):
    """A monthly spending limit for a category (API_CONTRACT.md §4)."""

    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("category", "month", name="uq_budgets_category_month"),
        CheckConstraint("amount_cents > 0", name="ck_budgets_amount_cents_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return (
            f"Budget(id={self.id!r}, category={self.category!r}, "
            f"month={self.month!r}, amount_cents={self.amount_cents!r})"
        )
