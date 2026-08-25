"""Transactions page: create, edit, delete, list, and filter transactions.

Talks to the backend exclusively through api_client, per
API_CONTRACT.md §2. Validation is backend-owned — this page only
surfaces the `detail` message the API returns on a bad request; it
does not re-implement that validation itself. Filtering is likewise
backend-owned: the widgets below only choose which query params to
send, via filters.build_transaction_filters (SCRUM-10).
"""

from datetime import date as date_cls

import streamlit as st

import api_client
from filters import ALL_CATEGORIES, TRANSACTION_TYPE_FILTER_OPTIONS, build_transaction_filters
from formatting import cents_to_dollars, dollars_to_cents, format_cents

TRANSACTION_TYPES = ["expense", "income"]


def _category_options() -> list[str]:
    try:
        categories = api_client.get_categories()
    except api_client.APIError as exc:
        st.warning(f"Could not load categories: {exc}")
        return []
    return [category["name"] for category in categories]


def _category_field(category_options: list[str], *, value: str | None = None):
    if not category_options:
        return st.text_input("Category", value=value or "")
    index = category_options.index(value) if value in category_options else 0
    return st.selectbox("Category", category_options, index=index)


def _render_create_form(category_options: list[str]) -> None:
    st.subheader("Add transaction")
    with st.form("create_transaction", clear_on_submit=True):
        txn_date = st.date_input("Date", value=date_cls.today())
        description = st.text_input("Description")
        category = _category_field(category_options)
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
        txn_type = st.selectbox("Type", TRANSACTION_TYPES)
        submitted = st.form_submit_button("Add transaction")

    if not submitted:
        return

    try:
        api_client.create_transaction(
            date=txn_date.isoformat(),
            description=description,
            category=category,
            amount_cents=dollars_to_cents(amount),
            type_=txn_type,
        )
    except api_client.APIError as exc:
        st.error(str(exc))
    else:
        st.success("Transaction added.")
        st.rerun()


def _render_filters(category_options: list[str]) -> dict:
    st.subheader("Filters")
    col1, col2, col3, col4 = st.columns(4)
    category = col1.selectbox("Category", [ALL_CATEGORIES] + category_options)
    txn_type = col2.selectbox("Type", TRANSACTION_TYPE_FILTER_OPTIONS)
    start_date = col3.date_input("Start date", value=None)
    end_date = col4.date_input("End date", value=None)
    return build_transaction_filters(category, txn_type, start_date, end_date)


def _render_transaction_list(filters: dict) -> list[dict]:
    st.subheader("All transactions")
    try:
        transactions = api_client.list_transactions(**filters)
    except api_client.APIError as exc:
        st.error(f"Could not load transactions: {exc}")
        return []

    if not transactions:
        st.info("No transactions match the current filters." if any(filters.values()) else "No transactions yet.")
        return []

    st.dataframe(
        [
            {
                "ID": txn["id"],
                "Date": txn["date"],
                "Description": txn["description"],
                "Category": txn["category"],
                "Type": txn["type"],
                "Amount": format_cents(txn["amount_cents"]),
            }
            for txn in transactions
        ],
        hide_index=True,
        width="stretch",
    )
    return transactions


def _render_edit_delete_section(transactions: list[dict], category_options: list[str]) -> None:
    st.subheader("Edit or delete a transaction")
    if not transactions:
        st.caption("Add a transaction above to edit or delete it here.")
        return

    options = {f"#{txn['id']} — {txn['date']} — {txn['description']}": txn for txn in transactions}
    label = st.selectbox("Select a transaction", list(options.keys()))
    transaction = options[label]

    with st.form("edit_transaction"):
        txn_date = st.date_input("Date", value=date_cls.fromisoformat(transaction["date"]))
        description = st.text_input("Description", value=transaction["description"])
        category = _category_field(category_options, value=transaction["category"])
        amount = st.number_input(
            "Amount ($)",
            min_value=0.01,
            step=0.01,
            format="%.2f",
            value=cents_to_dollars(transaction["amount_cents"]),
        )
        txn_type = st.selectbox(
            "Type", TRANSACTION_TYPES, index=TRANSACTION_TYPES.index(transaction["type"])
        )
        confirm_delete = st.checkbox("Confirm delete — this cannot be undone")
        col1, col2 = st.columns(2)
        update_clicked = col1.form_submit_button("Update")
        delete_clicked = col2.form_submit_button("Delete")

    if update_clicked:
        try:
            api_client.update_transaction(
                transaction["id"],
                date=txn_date.isoformat(),
                description=description,
                category=category,
                amount_cents=dollars_to_cents(amount),
                type_=txn_type,
            )
        except api_client.APIError as exc:
            st.error(str(exc))
        else:
            st.success("Transaction updated.")
            st.rerun()

    if delete_clicked:
        if not confirm_delete:
            st.warning("Check 'Confirm delete' first to delete this transaction.")
        else:
            try:
                api_client.delete_transaction(transaction["id"])
            except api_client.APIError as exc:
                st.error(str(exc))
            else:
                st.success("Transaction deleted.")
                st.rerun()


def render() -> None:
    st.title("Transactions")
    category_options = _category_options()
    _render_create_form(category_options)
    filters = _render_filters(category_options)
    transactions = _render_transaction_list(filters)
    _render_edit_delete_section(transactions, category_options)
