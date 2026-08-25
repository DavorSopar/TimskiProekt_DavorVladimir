"""CSV Import page: upload a CSV and show the backend's import results.

Talks to the backend exclusively through api_client, per
API_CONTRACT.md §5. Row validation is entirely backend-owned — this
page uploads the file as-is and displays the `errors` array the API
returns; it never validates or parses CSV rows itself.
"""

import streamlit as st

import api_client


def render() -> None:
    st.title("CSV Import")

    st.caption(
        "Columns, in order: date, description, category, amount, type. "
        "See API_CONTRACT.md §5 for the full locked format."
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is None:
        return

    if not st.button("Import"):
        return

    try:
        result = api_client.import_csv(uploaded_file.name, uploaded_file.getvalue())
    except api_client.APIError as exc:
        st.error(str(exc))
        return

    st.success(f"Imported {result['imported']} row(s). Skipped {result['skipped']} row(s).")

    errors = result.get("errors") or []
    if errors:
        st.subheader("Errors")
        st.dataframe(
            [{"Row": error["row"], "Message": error["message"]} for error in errors],
            hide_index=True,
            width="stretch",
        )
