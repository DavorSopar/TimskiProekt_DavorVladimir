# Personal Finance Tracker

A lightweight personal finance tracker: FastAPI + SQLAlchemy + SQLite backend
with a Streamlit UI.

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python 3.12 is installed automatically by uv)

## Setup

```bash
uv sync
```

This creates `.venv/` and installs the exact versions pinned in `uv.lock`.

## Running the app

The backend and the Streamlit UI are two separate processes. Run each in
its own terminal, from the repository root.

**1. Start the backend** (creates the local SQLite database and seeds a
default category set on first run):

```bash
uv run uvicorn app.main:app --reload
```

Serves at `http://127.0.0.1:8000`, with every endpoint under `/api`.

**2. Start the Streamlit UI**, in a second terminal:

```bash
uv run streamlit run app/streamlit/app.py
```

Opens at `http://localhost:8501`. The UI reads the backend's base URL from
the `FINANCE_API_URL` environment variable, defaulting to
`http://127.0.0.1:8000` if unset — so a fresh clone works with no
configuration as long as the backend is running on its default port. To
point the UI at a different backend:

```bash
FINANCE_API_URL="http://127.0.0.1:9000" uv run streamlit run app/streamlit/app.py
```

The sidebar shows whether the UI can currently reach the backend.

## Tests

```bash
uv run pytest
```

Runs both the backend test suite and the Streamlit/API-client test suite
together.

## Project layout

```
app/
  main.py         FastAPI application entry point
  api/            FastAPI routers and Pydantic schemas
  database/       SQLAlchemy engine, session, models, seed data
  services/       backend business logic (budgets, analytics, CSV import)
  streamlit/      Streamlit UI
    app.py            entry point / page navigation / connectivity check
    api_client.py      the only module that calls the backend over HTTP
    formatting.py      cents <-> dollars conversion and display
    filters.py         transaction filter-widget -> query-param mapping
    budget_helpers.py  month formatting, budget-by-category lookup
    csv_import_helpers.py  CSV import result message classification
    views/             one module per page: dashboard, transactions,
                        budgets, csv_import, analytics
tests/            backend tests + Streamlit/API-client tests
data/             local SQLite database file (git-ignored)
```

## CSV import format

The importer expects a header row with exactly these columns, in this
order: `date,description,category,amount,type`. See `API_CONTRACT.md` §5
for the full locked format and error-reporting behavior.

## Reference documents

These live in the repository root but are intentionally **not tracked in
git** (see `.gitignore`) — they're per-participant working references from
the assignment setup, not shared project files. Each participant should
already have their own local copy:

- `API_CONTRACT.md` — locked backend/frontend interface (endpoints, schemas,
  CSV format). Authoritative for anything the UI or API disagree on.
- `CLAUDE-PARTICIPANT-1.md` / `CLAUDE-PARTICIPANT-2.md` — each participant's
  working agreement (backend vs. Streamlit frontend ownership, workflow
  rules).
