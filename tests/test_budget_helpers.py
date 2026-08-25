"""Tests for the pure Budgets-page helpers (SCRUM-12)."""

from datetime import date

from app.streamlit.budget_helpers import find_budget_for_category, month_string


def test_month_string_formats_single_digit_month_with_zero_pad():
    assert month_string(date(2025, 1, 5)) == "2025-01"


def test_month_string_formats_double_digit_month():
    assert month_string(date(2025, 11, 30)) == "2025-11"


def test_find_budget_for_category_returns_match():
    budgets = [
        {"id": 1, "category": "Food", "month": "2025-01", "amount_cents": 20000},
        {"id": 2, "category": "Rent", "month": "2025-01", "amount_cents": 150000},
    ]
    assert find_budget_for_category(budgets, "Rent")["id"] == 2


def test_find_budget_for_category_returns_none_when_missing():
    budgets = [{"id": 1, "category": "Food", "month": "2025-01", "amount_cents": 20000}]
    assert find_budget_for_category(budgets, "Rent") is None


def test_find_budget_for_category_handles_empty_list():
    assert find_budget_for_category([], "Food") is None
