"""Pure helpers for the Budgets page.

Kept separate from view code so this logic is easy to unit test without
a Streamlit runtime. spent/remaining/over-budget figures are never
computed here — those always come from GET /api/budgets/{id}/status
(API_CONTRACT.md §4).
"""

from __future__ import annotations

from datetime import date


def month_string(value: date) -> str:
    """Format a date as the YYYY-MM string API_CONTRACT.md §4 expects."""
    return value.strftime("%Y-%m")


def find_budget_for_category(budgets: list[dict], category: str) -> dict | None:
    """Return the budget matching `category` from a list of Budget dicts, if any."""
    for budget in budgets:
        if budget["category"] == category:
            return budget
    return None
