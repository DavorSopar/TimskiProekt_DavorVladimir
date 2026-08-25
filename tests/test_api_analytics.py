"""Tests for the analytics API (SCRUM-15, API_CONTRACT.md §6)."""

from datetime import date


def _create_transaction(client, **overrides):
    fields = {
        "date": "2025-01-15",
        "description": "Groceries",
        "category": "Food",
        "amount_cents": 4250,
        "type": "expense",
    }
    fields.update(overrides)
    return client.post("/api/transactions", json=fields)


def test_summary_totals_income_expenses_and_net_balance(client):
    _create_transaction(client, type="income", amount_cents=300000)
    _create_transaction(client, type="expense", amount_cents=4250)
    _create_transaction(client, type="expense", amount_cents=1000)

    response = client.get("/api/analytics/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_income_cents"] == 300000
    assert body["total_expenses_cents"] == 5250
    assert body["net_balance_cents"] == 294750


def test_summary_filters_by_date_range(client):
    _create_transaction(client, date="2025-01-01", type="income", amount_cents=1000)
    _create_transaction(client, date="2025-06-01", type="income", amount_cents=2000)

    response = client.get(
        "/api/analytics/summary", params={"start_date": "2025-01-01", "end_date": "2025-03-01"}
    )

    assert response.status_code == 200
    assert response.json()["total_income_cents"] == 1000


def test_by_category_is_expenses_only_sorted_descending(client):
    _create_transaction(client, category="Food", type="expense", amount_cents=1000)
    _create_transaction(client, category="Rent", type="expense", amount_cents=5000)
    _create_transaction(client, category="Food", type="income", amount_cents=999999)

    response = client.get("/api/analytics/by-category")

    assert response.status_code == 200
    body = response.json()
    assert body == [
        {"category": "Rent", "total_cents": 5000},
        {"category": "Food", "total_cents": 1000},
    ]


def test_monthly_trend_includes_current_month_totals(client):
    today = date.today()
    current_month = f"{today.year:04d}-{today.month:02d}"
    _create_transaction(client, date=today.isoformat(), type="income", amount_cents=100000)
    _create_transaction(client, date=today.isoformat(), type="expense", amount_cents=5000)

    response = client.get("/api/analytics/monthly-trend", params={"months": 3})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    current = next(m for m in body if m["month"] == current_month)
    assert current["income_cents"] == 100000
    assert current["expenses_cents"] == 5000


def test_monthly_trend_defaults_to_six_months(client):
    response = client.get("/api/analytics/monthly-trend")

    assert response.status_code == 200
    assert len(response.json()) == 6
