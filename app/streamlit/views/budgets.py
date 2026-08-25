"""Budgets page: select a month/category, create or update its budget,
and show current spending/remaining/over-budget status.

Talks to the backend exclusively through api_client, per
API_CONTRACT.md §4. spent_cents/remaining_cents/over_budget always come
from GET /api/budgets/{id}/status — this page never recomputes them
from a raw transaction list.
"""

from datetime import date as date_cls

import streamlit as st

import api_client
from budget_helpers import find_budget_for_category, month_string
from formatting import cents_to_dollars, dollars_to_cents, format_cents


def _category_options() -> list[str]:
    try:
        categories = api_client.get_categories()
    except api_client.APIError as exc:
        st.warning(f"Could not load categories: {exc}")
        return []
    return [category["name"] for category in categories]


def _render_status(budget_id: int) -> None:
    try:
        status = api_client.get_budget_status(budget_id)
    except api_client.APIError as exc:
        st.error(f"Could not load budget status: {exc}")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Budget", format_cents(status["budget"]["amount_cents"]))
    col2.metric("Spent", format_cents(status["spent_cents"]))
    col3.metric("Remaining", format_cents(status["remaining_cents"]))

    if status["over_budget"]:
        st.error("⚠️ Over budget for this category and month.")
    else:
        st.success("Within budget.")


def render() -> None:
    st.title("Budgets")

    category_options = _category_options()
    if not category_options:
        st.info("No categories available yet.")
        return

    col1, col2 = st.columns(2)
    month_date = col1.date_input("Month", value=date_cls.today())
    category = col2.selectbox("Category", category_options)
    month = month_string(month_date)

    try:
        month_budgets = api_client.list_budgets(month=month)
    except api_client.APIError as exc:
        st.error(f"Could not load budgets: {exc}")
        month_budgets = []

    existing = find_budget_for_category(month_budgets, category)

    st.subheader("Set budget")
    default_amount = cents_to_dollars(existing["amount_cents"]) if existing else 0.01
    with st.form("set_budget"):
        amount = st.number_input(
            "Budget amount ($)",
            min_value=0.01,
            step=0.01,
            format="%.2f",
            value=default_amount,
        )
        submitted = st.form_submit_button("Save budget")

    if submitted:
        amount_cents = dollars_to_cents(amount)
        try:
            if existing:
                api_client.update_budget(existing["id"], amount_cents=amount_cents)
            else:
                api_client.create_budget(category=category, month=month, amount_cents=amount_cents)
        except api_client.APIError as exc:
            st.error(str(exc))
        else:
            st.success("Budget saved.")
            st.rerun()

    st.subheader("Status")
    if existing:
        _render_status(existing["id"])
    else:
        st.info("No budget set yet for this category and month.")

    st.subheader(f"All budgets for {month}")
    if month_budgets:
        st.dataframe(
            [
                {"Category": budget["category"], "Budget": format_cents(budget["amount_cents"])}
                for budget in month_budgets
            ],
            hide_index=True,
            width="stretch",
        )
    else:
        st.caption("No budgets set for this month yet.")
