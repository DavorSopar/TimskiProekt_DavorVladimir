"""Entry point for the Personal Finance Tracker Streamlit app.

Wires up the multipage navigation skeleton (SCRUM-02) and a basic backend
connectivity check (SCRUM-06). Page content, further API calls, and
business logic land in later Jira issues.

Run with:

    uv run streamlit run app/streamlit/app.py

The backend base URL is read from the FINANCE_API_URL environment
variable, defaulting to http://127.0.0.1:8000 (see API_CONTRACT.md §1).
"""

import streamlit as st

from api_client import APIError, get_base_url, get_categories
from views import analytics, budgets, csv_import, dashboard, transactions

st.set_page_config(page_title="Personal Finance Tracker", layout="wide")

pages = [
    st.Page(dashboard.render, title="Dashboard", url_path="dashboard", default=True),
    st.Page(transactions.render, title="Transactions", url_path="transactions"),
    st.Page(budgets.render, title="Budgets", url_path="budgets"),
    st.Page(csv_import.render, title="CSV Import", url_path="csv-import"),
    st.Page(analytics.render, title="Analytics", url_path="analytics"),
]

with st.sidebar:
    st.caption(f"Backend: {get_base_url()}")
    try:
        get_categories()
    except APIError as exc:
        st.error(f"Backend unreachable: {exc}")
    else:
        st.success("Connected to backend")

st.navigation(pages).run()
