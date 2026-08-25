"""Tests for the transaction filter-mapping helper (SCRUM-10)."""

from datetime import date

from app.streamlit.filters import ALL_CATEGORIES, ALL_TYPES, build_transaction_filters


def test_all_sentinels_produce_no_filters():
    result = build_transaction_filters(ALL_CATEGORIES, ALL_TYPES, None, None)
    assert result == {
        "category": None,
        "type_": None,
        "start_date": None,
        "end_date": None,
    }


def test_specific_category_and_type_pass_through():
    result = build_transaction_filters("Food", "expense", None, None)
    assert result["category"] == "Food"
    assert result["type_"] == "expense"


def test_dates_are_serialized_to_iso_strings():
    result = build_transaction_filters(
        ALL_CATEGORIES, ALL_TYPES, date(2025, 1, 1), date(2025, 1, 31)
    )
    assert result["start_date"] == "2025-01-01"
    assert result["end_date"] == "2025-01-31"


def test_missing_dates_stay_none():
    result = build_transaction_filters(ALL_CATEGORIES, ALL_TYPES, None, None)
    assert result["start_date"] is None
    assert result["end_date"] is None
