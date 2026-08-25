"""Supplementary backend coverage (SCRUM-18): validation edge cases, empty-data
behavior, and status codes not already exercised by the per-endpoint test files.
"""


def _transaction_payload(**overrides):
    fields = {
        "date": "2025-01-15",
        "description": "Groceries",
        "category": "Food",
        "amount_cents": 4250,
        "type": "expense",
    }
    fields.update(overrides)
    return fields


# --- Transactions: PUT validation -------------------------------------------------


def test_put_transaction_with_invalid_type_returns_422(client):
    created = client.post("/api/transactions", json=_transaction_payload()).json()

    response = client.put(
        f"/api/transactions/{created['id']}", json=_transaction_payload(type="transfer")
    )

    assert response.status_code == 422


def test_list_transactions_empty_returns_empty_list(client):
    response = client.get("/api/transactions")

    assert response.status_code == 200
    assert response.json() == []


# --- Categories: validation ---------------------------------------------------


def test_create_category_missing_name_returns_422(client):
    response = client.post("/api/categories", json={})

    assert response.status_code == 422


# --- Budgets: validation -------------------------------------------------------


def test_create_budget_non_positive_amount_returns_422(client):
    response = client.post(
        "/api/budgets", json={"category": "Food", "month": "2025-01", "amount_cents": 0}
    )

    assert response.status_code == 422


def test_update_budget_non_positive_amount_returns_422(client):
    created = client.post(
        "/api/budgets", json={"category": "Food", "month": "2025-01", "amount_cents": 10000}
    ).json()

    response = client.put(f"/api/budgets/{created['id']}", json={"amount_cents": -1})

    assert response.status_code == 422


def test_budget_status_with_no_transactions_is_fully_remaining(client):
    created = client.post(
        "/api/budgets", json={"category": "Food", "month": "2025-01", "amount_cents": 10000}
    ).json()

    response = client.get(f"/api/budgets/{created['id']}/status")

    assert response.status_code == 200
    body = response.json()
    assert body["spent_cents"] == 0
    assert body["remaining_cents"] == 10000
    assert body["over_budget"] is False


# --- CSV import: edge cases -----------------------------------------------------


def test_import_csv_with_header_only_imports_nothing(client):
    csv_content = "date,description,category,amount,type\n"
    files = {"file": ("transactions.csv", csv_content, "text/csv")}

    response = client.post("/api/import/csv", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body == {"imported": 0, "skipped": 0, "errors": []}


def test_import_csv_without_file_returns_422(client):
    response = client.post("/api/import/csv")

    assert response.status_code == 422


# --- Analytics: empty-data behavior ---------------------------------------------


def test_summary_with_no_transactions_is_all_zero(client):
    response = client.get("/api/analytics/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_income_cents": 0,
        "total_expenses_cents": 0,
        "net_balance_cents": 0,
    }


def test_by_category_with_no_transactions_is_empty_list(client):
    response = client.get("/api/analytics/by-category")

    assert response.status_code == 200
    assert response.json() == []


def test_monthly_trend_with_no_transactions_still_returns_month_labels(client):
    response = client.get("/api/analytics/monthly-trend", params={"months": 2})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert all(m["income_cents"] == 0 and m["expenses_cents"] == 0 for m in body)


# --- Cross-cutting: 404s for unknown routes -------------------------------------


def test_unknown_route_returns_404(client):
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
