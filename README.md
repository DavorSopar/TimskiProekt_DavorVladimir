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

## Tests

```bash
uv run pytest
```

## Project layout

```
app/
  api/          FastAPI routers and Pydantic schemas
  database/     SQLAlchemy engine, session, models, data access
  services/     business logic (budgets, analytics, CSV import)
  streamlit/    Streamlit pages and UI components
tests/          backend tests
```

## Reference documents

- `API_CONTRACT.md` — locked backend/frontend interface (endpoints, schemas, CSV format)
- `CLAUDE-PARTICIPANT-1.md` — backend working agreement
