"""Dashboard page: at-a-glance income, expenses, net balance, top
spending categories, and a monthly spending summary.

Talks to the backend exclusively through api_client, per
API_CONTRACT.md §6. All totals are backend-computed — this page never
re-derives them from a raw transaction list. Charts belong to the
Analytics page (SCRUM-17); this page uses plain metrics/tables so it
stays a quick at-a-glance view.
"""

import streamlit as st

import api_client
from formatting import format_cents

TOP_CATEGORY_COUNT = 5


def _render_top_categories() -> None:
    st.subheader("Top spending categories")
    try:
        by_category = api_client.get_analytics_by_category()
    except api_client.APIError as exc:
        st.error(f"Could not load category spending: {exc}")
        return

    if not by_category:
        st.caption("No expenses recorded yet.")
        return

    st.dataframe(
        [
            {"Category": row["category"], "Spent": format_cents(row["total_cents"])}
            for row in by_category[:TOP_CATEGORY_COUNT]
        ],
        hide_index=True,
        width="stretch",
    )


def _render_monthly_summary() -> None:
    st.subheader("Monthly spending summary")
    try:
        monthly_trend = api_client.get_monthly_trend()
    except api_client.APIError as exc:
        st.error(f"Could not load monthly trend: {exc}")
        return

    if not monthly_trend:
        st.caption("No transaction history yet.")
        return

    st.dataframe(
        [
            {
                "Month": row["month"],
                "Income": format_cents(row["income_cents"]),
                "Expenses": format_cents(row["expenses_cents"]),
            }
            for row in monthly_trend
        ],
        hide_index=True,
        width="stretch",
    )


def render() -> None:
    st.title("Dashboard")

    try:
        summary = api_client.get_analytics_summary()
    except api_client.APIError as exc:
        st.error(f"Could not load dashboard: {exc}")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Income", format_cents(summary["total_income_cents"]))
    col2.metric("Expenses", format_cents(summary["total_expenses_cents"]))
    col3.metric("Net balance", format_cents(summary["net_balance_cents"]))

    _render_top_categories()
    _render_monthly_summary()
