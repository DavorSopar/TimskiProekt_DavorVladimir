"""Tests for the budget API (SCRUM-11, API_CONTRACT.md §4)."""


def _create_budget(client, **overrides):
    fields = {"category": "Food", "month": "2025-01", "amount_cents": 20000}
    fields.update(overrides)
    return client.post("/api/budgets", json=fields)


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


def test_create_budget_returns_201(client):
    response = _create_budget(client)

    assert response.status_code == 201
    body = response.json()
    assert body["category"] == "Food"
    assert body["month"] == "2025-01"
    assert body["amount_cents"] == 20000


def test_create_duplicate_category_month_returns_409(client):
    _create_budget(client)

    response = _create_budget(client)

    assert response.status_code == 409


def test_invalid_month_format_returns_422(client):
    response = _create_budget(client, month="2025/01")

    assert response.status_code == 422


def test_list_budgets_filters_by_month(client):
    _create_budget(client, category="Food", month="2025-01")
    _create_budget(client, category="Rent", month="2025-02")

    response = client.get("/api/budgets", params={"month": "2025-01"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "Food"


def test_update_budget_amount(client):
    created = _create_budget(client).json()

    response = client.put(f"/api/budgets/{created['id']}", json={"amount_cents": 30000})

    assert response.status_code == 200
    assert response.json()["amount_cents"] == 30000


def test_update_missing_budget_returns_404(client):
    response = client.put("/api/budgets/999", json={"amount_cents": 30000})

    assert response.status_code == 404


def test_budget_status_computes_spent_remaining_and_over_budget(client):
    created = _create_budget(client, amount_cents=10000).json()
    _create_transaction(client, amount_cents=4000)
    _create_transaction(client, amount_cents=3000)
    # different month, should not count
    _create_transaction(client, date="2025-02-01", amount_cents=100000)
    # income in same category/month, should not count
    _create_transaction(client, type="income", amount_cents=100000)

    response = client.get(f"/api/budgets/{created['id']}/status")

    assert response.status_code == 200
    body = response.json()
    assert body["budget"]["id"] == created["id"]
    assert body["spent_cents"] == 7000
    assert body["remaining_cents"] == 3000
    assert body["over_budget"] is False


def test_budget_status_over_budget(client):
    created = _create_budget(client, amount_cents=1000).json()
    _create_transaction(client, amount_cents=5000)

    response = client.get(f"/api/budgets/{created['id']}/status")

    assert response.status_code == 200
    body = response.json()
    assert body["spent_cents"] == 5000
    assert body["remaining_cents"] == -4000
    assert body["over_budget"] is True


def test_budget_status_missing_budget_returns_404(client):
    response = client.get("/api/budgets/999/status")

    assert response.status_code == 404
