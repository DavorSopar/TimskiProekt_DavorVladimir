"""Pure helpers for turning filter-widget selections into API query params.

Kept separate from view code so this data-transformation logic is easy
to unit test without a Streamlit runtime. The backend still owns actual
filtering (API_CONTRACT.md §2: "filters combine with AND") — this module
only maps UI sentinel values ("All categories") to the `None` that means
"no filter" to api_client.list_transactions.
"""

from __future__ import annotations

from datetime import date

ALL_CATEGORIES = "All categories"
ALL_TYPES = "All types"
TRANSACTION_TYPE_FILTER_OPTIONS = [ALL_TYPES, "expense", "income"]


def build_transaction_filters(
    category: str,
    transaction_type: str,
    start_date: date | None,
    end_date: date | None,
) -> dict:
    """Map transaction-list filter widget values to list_transactions() kwargs."""
    return {
        "category": None if category == ALL_CATEGORIES else category,
        "type_": None if transaction_type == ALL_TYPES else transaction_type,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
    }
