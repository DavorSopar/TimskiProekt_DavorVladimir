# API Contract — Personal Finance Tracker

This document is the single source of truth for the interface between the
FastAPI backend (Participant 1) and the Streamlit frontend (Participant 2).

**Rule: neither participant invents a new field, endpoint, or status code
independently.** If the UI needs something not listed here, open/update a
Jira issue and amend this document as part of that issue — don't build a
private workaround.

Both `CLAUDE-PARTICIPANT-1.md` and `CLAUDE-PARTICIPANT-2.md` sessions should
read this file before starting any FIN-07 through FIN-15 work.

---

## 1. Runtime Convention

- FastAPI runs at `http://127.0.0.1:8000` in local dev.
- Streamlit reads the base URL from an environment variable
  `FINANCE_API_URL`, defaulting to `http://127.0.0.1:8000` if unset.
- All endpoints are prefixed with `/api`.
- All request/response bodies are JSON except CSV upload, which is
  `multipart/form-data`.
- All dates are ISO 8601 strings, `YYYY-MM-DD`, no time component, no timezone.
- Money is transmitted as a JSON number representing whole cents
  (integer), not dollars-as-float. Example: `$42.50` → `4250`.
  UI is responsible for formatting cents back to a dollar display.

## 2. Transactions

### Model

```
Transaction:
  id: int
  date: string (YYYY-MM-DD)
  description: string
  category: string
  amount_cents: int          # positive integer; sign is derived from type
  type: "income" | "expense"
  created_at: string (ISO 8601 datetime)
```

### Endpoints

| Method | Path | Body | Success | Notes |
|---|---|---|---|---|
| POST | `/api/transactions` | `{date, description, category, amount_cents, type}` | 201, returns Transaction | |
| GET | `/api/transactions` | query params: `category`, `type`, `start_date`, `end_date` (all optional) | 200, returns `Transaction[]` | filters combine with AND |
| GET | `/api/transactions/{id}` | — | 200 Transaction / 404 | |
| PUT | `/api/transactions/{id}` | same body as POST | 200 Transaction / 404 | full replace, not partial patch |
| DELETE | `/api/transactions/{id}` | — | 204 / 404 | |

### Validation errors

- Invalid body → `422` with FastAPI's default Pydantic error shape
  (Streamlit reads `detail` and displays the first message per field).
- `amount_cents` must be a positive integer; `type` must be exactly
  `"income"` or `"expense"`.

## 3. Categories

### Model

```
Category:
  id: int
  name: string
```

### Endpoints

| Method | Path | Body | Success |
|---|---|---|---|
| GET | `/api/categories` | — | 200, `Category[]` |
| POST | `/api/categories` | `{name}` | 201 Category / 409 if name exists |
| DELETE | `/api/categories/{id}` | — | 204 / 404 / 409 if in use by a transaction |

Decision (locks the ambiguity from the CLAUDE.md files): **categories are
user-manageable**, not a fixed enum. A small default seed set (e.g. Food,
Rent, Transport, Utilities, Income, Other) is inserted on first DB creation
so the UI isn't empty on a fresh clone.

## 4. Budgets

### Model

```
Budget:
  id: int
  category: string
  month: string (YYYY-MM)
  amount_cents: int          # the budget limit
```

### Endpoints

| Method | Path | Body | Success |
|---|---|---|---|
| POST | `/api/budgets` | `{category, month, amount_cents}` | 201 Budget / 409 if category+month already has a budget (use PUT to change it) |
| GET | `/api/budgets` | query param: `month` (optional) | 200, `Budget[]` |
| PUT | `/api/budgets/{id}` | `{amount_cents}` | 200 Budget / 404 |
| GET | `/api/budgets/{id}/status` | — | 200: `{budget: Budget, spent_cents: int, remaining_cents: int, over_budget: bool}` |

`spent_cents` is computed server-side from transactions in that category
and month — the UI never sums this itself.

## 5. CSV Import

### Locked CSV format

```csv
date,description,category,amount,type
2025-01-15,Groceries,Food,42.50,expense
2025-01-16,Paycheck,Income,2500.00,income
```

- Header row required, exact column names above, in this order.
- `date`: `YYYY-MM-DD`.
- `amount`: plain decimal string, always positive (sign comes from `type`).
- `type`: `income` or `expense`, case-sensitive lowercase.
- `category`: matched by name against existing categories; unknown
  categories are auto-created (not rejected) — simplest behavior for a
  lightweight tool.

### Endpoint

| Method | Path | Body | Success |
|---|---|---|---|
| POST | `/api/import/csv` | multipart file field `file` | 200: `{imported: int, skipped: int, errors: [{row: int, message: string}]}` |

Import is all-or-nothing per row, not all-or-nothing for the file: valid
rows are persisted even if other rows fail validation. The UI displays the
`errors` array to the user.

## 6. Analytics

| Method | Path | Query params | Response |
|---|---|---|---|
| GET | `/api/analytics/summary` | `start_date`, `end_date` (optional) | `{total_income_cents, total_expenses_cents, net_balance_cents}` |
| GET | `/api/analytics/by-category` | `start_date`, `end_date` (optional) | `[{category, total_cents}]`, expenses only, sorted descending |
| GET | `/api/analytics/monthly-trend` | `months` (optional int, default 6) | `[{month: "YYYY-MM", income_cents, expenses_cents}]` |

All analytics are backend-computed. The UI never re-derives totals from a
raw transaction list — it only renders what these endpoints return.

## 7. Error Shape (all endpoints)

```
{
  "detail": "human readable message"
}
```

or, for validation (422), FastAPI's default:

```
{
  "detail": [{"loc": [...], "msg": "...", "type": "..."}]
}
```

## 8. Amending This Contract

If a Jira issue requires changing anything above:
1. Update this file in the same PR as the implementation.
2. Note the change in the PR description.
3. The other participant should not need to guess — if their session hits
   a mismatch between this doc and reality, that's a bug, not a feature
   to work around.

## 9. Shared-File Edit Protocol

For `pyproject.toml`, `.gitignore`, `README.md`, and top-level wiring files:

- Pull `develop` immediately before editing any shared file — do not batch
  a shared-file edit into a feature branch that's been open a while.
- Dependency additions (`uv add ...`) go in their own small commit, not
  mixed with feature code, so they're easy to review and rarely conflict.
- If both of you need to touch the same shared file in the same work
  session, whoever finishes first pushes and opens the PR immediately;
  the other rebases onto the updated `develop` before continuing, rather
  than both PRs racing against a stale base.
