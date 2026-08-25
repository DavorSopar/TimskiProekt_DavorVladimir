"""Pydantic request/response schemas.

Shapes must match API_CONTRACT.md exactly — do not add or rename fields
here without updating that document in the same change.
"""

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

TransactionType = Literal["income", "expense"]


class TransactionCreate(BaseModel):
    """Request body for POST/PUT /api/transactions (API_CONTRACT.md §2)."""

    date: date
    description: str
    category: str
    amount_cents: int = Field(gt=0)
    type: TransactionType


class TransactionRead(BaseModel):
    """Response body for transaction endpoints (API_CONTRACT.md §2)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    description: str
    category: str
    amount_cents: int
    type: TransactionType
    created_at: datetime


class CategoryCreate(BaseModel):
    """Request body for POST /api/categories (API_CONTRACT.md §3)."""

    name: str


class CategoryRead(BaseModel):
    """Response body for category endpoints (API_CONTRACT.md §3)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


MonthStr = Annotated[str, Field(pattern=r"^\d{4}-\d{2}$")]


class BudgetCreate(BaseModel):
    """Request body for POST /api/budgets (API_CONTRACT.md §4)."""

    category: str
    month: MonthStr
    amount_cents: int = Field(gt=0)


class BudgetUpdate(BaseModel):
    """Request body for PUT /api/budgets/{id} (API_CONTRACT.md §4)."""

    amount_cents: int = Field(gt=0)


class BudgetRead(BaseModel):
    """Response body for budget endpoints (API_CONTRACT.md §4)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    month: str
    amount_cents: int


class BudgetStatus(BaseModel):
    """Response body for GET /api/budgets/{id}/status (API_CONTRACT.md §4)."""

    budget: BudgetRead
    spent_cents: int
    remaining_cents: int
    over_budget: bool
