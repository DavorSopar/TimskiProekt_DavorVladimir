"""Entry point for the Personal Finance Tracker Streamlit app.

FIN-02 scope: this module wires up the multipage navigation skeleton only.
Every page is currently a placeholder — real content, API calls, and
business logic are added in later Jira issues (starting with FIN-06 for
the API client).

Run with:

    uv run streamlit run app/streamlit/app.py
"""

import streamlit as st

from views import analytics, budgets, csv_import, dashboard, transactions

st.set_page_config(page_title="Personal Finance Tracker", layout="wide")

pages = [
    st.Page(dashboard.render, title="Dashboard", url_path="dashboard", default=True),
    st.Page(transactions.render, title="Transactions", url_path="transactions"),
    st.Page(budgets.render, title="Budgets", url_path="budgets"),
    st.Page(csv_import.render, title="CSV Import", url_path="csv-import"),
    st.Page(analytics.render, title="Analytics", url_path="analytics"),
]

st.navigation(pages).run()
