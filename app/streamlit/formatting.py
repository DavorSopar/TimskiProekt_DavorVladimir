"""Shared money-formatting helpers for Streamlit pages.

Money crosses the API boundary as integer cents (API_CONTRACT.md §1).
These are the only two functions that should ever convert between that
wire format and the dollar amounts a user types or sees — pages should
import them rather than doing the arithmetic inline.
"""

from __future__ import annotations


def cents_to_dollars(cents: int) -> float:
    """Convert integer cents from the API into a plain dollar amount."""
    return cents / 100


def dollars_to_cents(amount: float) -> int:
    """Convert a dollar amount typed in the UI into integer cents for the API."""
    return round(amount * 100)


def format_cents(cents: int) -> str:
    """Format integer cents as a dollar display string.

    4250 -> '$42.50'; -5000 -> '-$50.00' (negative remaining/over-budget
    amounts read as a leading minus sign, not a minus inside the dollar sign).
    """
    dollars = cents_to_dollars(abs(cents))
    sign = "-" if cents < 0 else ""
    return f"{sign}${dollars:,.2f}"
