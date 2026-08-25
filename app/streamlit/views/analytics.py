"""Analytics page: charts for category spending and the monthly
income/expenses trend.

Talks to the backend exclusively through api_client, per
API_CONTRACT.md §6. All figures are backend-computed; this page only
turns them into charts — it never re-derives a total from a raw
transaction list.
"""

import streamlit as st

import api_client
from formatting import cents_to_dollars

MONTHLY_TREND_MONTHS = 6


def _render_category_chart() -> None:
    st.subheader("Spending by category")
    try:
        by_category = api_client.get_analytics_by_category()
    except api_client.APIError as exc:
        st.error(f"Could not load category spending: {exc}")
        return

    if not by_category:
        st.caption("No expenses recorded yet.")
        return

    chart_data = [
        {"Category": row["category"], "Spent": cents_to_dollars(row["total_cents"])}
        for row in by_category
    ]
    st.bar_chart(chart_data, x="Category", y="Spent")


def _render_monthly_trend_chart() -> None:
    st.subheader("Monthly spending trend")
    try:
        monthly_trend = api_client.get_monthly_trend(months=MONTHLY_TREND_MONTHS)
    except api_client.APIError as exc:
        st.error(f"Could not load monthly trend: {exc}")
        return

    if not monthly_trend:
        st.caption("No transaction history yet.")
        return

    chart_data = [
        {
            "Month": row["month"],
            "Income": cents_to_dollars(row["income_cents"]),
            "Expenses": cents_to_dollars(row["expenses_cents"]),
        }
        for row in monthly_trend
    ]
    st.line_chart(chart_data, x="Month", y=["Income", "Expenses"])


def render() -> None:
    st.title("Analytics")
    _render_category_chart()
    _render_monthly_trend_chart()
