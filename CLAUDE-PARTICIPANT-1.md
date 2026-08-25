# Claude Code Instructions — Participant 1

## Role

You are Participant 1 on a two-person software team building a lightweight Personal Finance Tracker.

Your primary ownership is the **backend, persistence, business logic, API, and backend testing**.

Do not take ownership of the Streamlit UI unless a task explicitly requires a small integration change.

## Required Reading Before Coding

Before starting any issue from FIN-07 through FIN-15, read `API_CONTRACT.md` in
the repository root in addition to this file. That document is the locked,
authoritative shape of every endpoint, request/response schema, status code,
and the CSV format. Do not invent or change a field name, endpoint path, or
response shape that differs from it — if an issue seems to require a change,
update `API_CONTRACT.md` in the same PR as the implementation and note the
change in the PR description. Participant 2's session builds against this
document, not against your running code, so drift here breaks integration
silently until FIN-20.

## Project Goal

Build a small, reliable personal finance application using:

- Python
- uv
- FastAPI
- SQLAlchemy
- SQLite
- Streamlit
- pytest

The application is deliberately lightweight. Do not introduce unnecessary infrastructure or features.

## Locked Scope

The application must support:

1. Transactions
   - create transaction
   - edit transaction
   - delete transaction
   - list transactions
   - transaction type: income or expense
   - amount, date, description, category
2. Categories
   - user-manageable (create/list/delete) — see `API_CONTRACT.md` §3.
     A small default seed set is inserted on first DB creation so the app
     isn't empty on a fresh clone.
3. Budgets
   - monthly budget per category
   - budget amount
   - amount spent
   - remaining/over-budget calculation
4. CSV import
   - import the locked CSV format in `API_CONTRACT.md` §5
   - validate rows before persistence; valid rows persist even if other rows fail
5. Analytics
   - total income
   - total expenses
   - net balance
   - spending by category
   - monthly spending trend
6. Streamlit pages
   - dashboard
   - transactions
   - budgets
   - CSV import
   - analytics

Out of scope:

- authentication or user accounts
- JWT
- PostgreSQL
- Docker/Docker Compose
- Redis
- background jobs
- external APIs
- banking integrations
- advanced accounting
- multi-user permissions
- deployment infrastructure

Do not add out-of-scope functionality unless the other developer or the project owner explicitly requests it.

## Architecture Ownership

Participant 1 owns:

- `app/api/`
- `app/database/`
- `app/services/`
- backend-facing tests
- database schema and persistence decisions
- FastAPI routes and Pydantic schemas
- keeping `API_CONTRACT.md` in sync with the actual API

Participant 2 owns:

- `app/streamlit/`
- Streamlit pages and UI components
- frontend-facing tests

Shared areas must be changed carefully:

- `pyproject.toml`
- `README.md`
- `.gitignore`
- top-level application wiring
- `API_CONTRACT.md`

Before changing shared files, inspect the latest `develop` branch and coordinate with the related Jira issue. See "Shared-File Edit Protocol" below.

## Runtime Convention

- FastAPI runs at `http://127.0.0.1:8000` in local dev, under an `/api` prefix.
- Streamlit reads the backend URL from `FINANCE_API_URL`, defaulting to
  `http://127.0.0.1:8000` — do not hardcode a different port or prefix.
- Money crosses the API as integer cents (`amount_cents`), never floats.
- Dates cross the API as `YYYY-MM-DD` strings, no time or timezone component.

Full detail lives in `API_CONTRACT.md`.

## Working in Parallel With Participant 2

Because your directories don't overlap, you and Participant 2 can work
simultaneously on separate feature branches without conflict — you don't
need to wait for each other to finish. A few things keep that safe:

- Pull `develop` before starting a new issue, as always.
- When merging into `develop`, merge one PR at a time rather than both at
  once — if your PR and Participant 2's are both ready close together,
  whichever merges second should pull the updated `develop` first.
- After merging a backend endpoint group into `develop`, do a quick real
  check that Streamlit can hit it successfully (not just that it matches
  the contract on paper) before considering the issue fully done. This
  catches drift early instead of at FIN-20.
- Treat shared-file edits according to the protocol below regardless of
  whether Participant 2 is actively working at the same time.

## Shared-File Edit Protocol

For `pyproject.toml`, `.gitignore`, `README.md`, `API_CONTRACT.md`, and
top-level wiring:

- Pull `develop` immediately before editing any of these — don't batch the
  edit into a feature branch that's been open a while.
- Keep dependency additions (`uv add ...`) or contract edits in their own
  small commit, separate from feature code.
- If you and Participant 2 both need to touch the same shared file around
  the same time, whichever of you finishes first pushes and opens the PR
  immediately; the other rebases onto the updated `develop` before
  continuing.

## Git Workflow

Branches:

- `main` — stable released code only
- `develop` — integration branch
- feature branches — one Jira issue or one tightly related unit of work

Use branch names like:

`feature/FIN-08-transaction-api`

Do not push directly to `main`.
Do not push directly to `develop` unless explicitly instructed for a release/integration action.
Do not force-push shared branches.

Before starting work:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/FIN-XX-short-description
```

Before committing:

```bash
uv run pytest
```

Use focused tests while developing and the full suite before opening a PR.

## Commit Rules

Use one or more focused commits per Jira issue.

Commit format:

`FIN-XX: short imperative description`

Examples:

- `FIN-08: implement transaction API`
- `FIN-09: add transaction validation`
- `FIN-16: add analytics service tests`

Do not create meaningless commits such as `changes`, `update`, or `stuff`.
Do not squash all work into one giant commit if the issue naturally contains separate implementation and test changes.

The Git author must be the real participant running this Claude session. Do not alter the other participant's Git identity.

## Push and Pull Request Ownership

Commit your work locally as issues are completed. Do not push to a remote
branch or open a pull request without the participant's explicit go-ahead
in the current session — surface what's ready to push and let them confirm
before it becomes visible on GitHub.

## Jira Rules

Every coding task must correspond to a Jira issue.

Before coding:

1. Read the Jira issue.
2. Understand its acceptance criteria.
3. Use its key in the branch name.
4. Use its key in commit messages.

When a task is completed:

- mention tests in the PR
- link the Jira issue
- move the issue according to the team's workflow

Do not mark unrelated Jira work as complete.

## API Rules

- Use FastAPI routers instead of placing all endpoints in one module.
- Use Pydantic models for request/response validation.
- Keep route handlers thin.
- Put business logic in services.
- Put database access in repository/data-access code rather than embedding SQL logic in route handlers.
- Return appropriate HTTP status codes.
- Validate amounts and dates.
- Do not trust imported CSV data.
- Avoid duplicated business rules.
- Match `API_CONTRACT.md` exactly; update it in the same PR if a deviation is genuinely required.

## Database Rules

SQLite is the locked database for this project.

- Use SQLAlchemy for persistence.
- Keep models explicit and simple.
- Store money as integer cents (see Runtime Convention above) — never store
  or persist unsafe floating-point representations of money.
- Validate data at the API/service boundary.
- Do not commit the local SQLite database file.

The project must be able to create its local database in a fresh clone without requiring an external database server.

## Testing Rules

Backend work requires tests.

Prioritize:

- transaction CRUD
- validation
- budget calculations
- analytics calculations
- CSV validation/import logic
- API status codes and response structures

Tests should be deterministic and independent.

## Definition of Done

A backend issue is done only when:

- implementation is complete
- tests cover the important behavior
- `uv run pytest` passes
- code follows the project architecture
- code matches `API_CONTRACT.md`, or the contract was updated in the same PR
- commit messages reference the Jira issue
- the branch is pushed (with participant confirmation)
- a pull request is opened against `develop`
- the PR description explains what changed and how it was tested

## Working With Participant 2

You are part of a real two-person workflow.

Do not overwrite or restructure Streamlit code simply because you would personally design it differently.

When the frontend requires an API change:

1. inspect the existing API and `API_CONTRACT.md`
2. preserve backwards compatibility where practical
3. update the API contract document and the implementation together
4. communicate the change through the Jira issue/PR
5. add or update tests

Prefer small integration boundaries over shared-file editing.

## Release Targets

### v0.1.0 — Foundation

- uv project
- FastAPI skeleton
- database setup
- SQLAlchemy models
- initial transaction API
- initial Streamlit application skeleton

### v0.2.0 — Core Finance

- complete transaction CRUD
- categories
- budgets
- CSV import
- validation
- core analytics

### v1.0.0 — Finished Application

- dashboard analytics
- charts
- polished filtering
- robust error handling
- test coverage for important paths
- documentation
- integration fixes

## Important Constraint

Do not expand the project.
The purpose is to complete a credible medium-difficulty application quickly while demonstrating professional GitHub/Jira collaboration.

When unsure between a simple and elaborate implementation, choose the simple implementation that satisfies the acceptance criteria.
