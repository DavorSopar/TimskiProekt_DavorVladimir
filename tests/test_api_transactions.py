"""Tests for the transaction CRUD API (SCRUM-07, API_CONTRACT.md §2)."""


def _payload(**overrides):
    fields = {
        "date": "2025-01-15",
        "description": "Groceries",
        "category": "Food",
        "amount_cents": 4250,
        "type": "expense",
    }
    fields.update(overrides)
    return fields


def test_create_transaction_returns_201(client):
    response = client.post("/api/transactions", json=_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["date"] == "2025-01-15"
    assert body["description"] == "Groceries"
    assert body["category"] == "Food"
    assert body["amount_cents"] == 4250
    assert body["type"] == "expense"
    assert "created_at" in body


def test_list_transactions_returns_created_transaction(client):
    client.post("/api/transactions", json=_payload())

    response = client.get("/api/transactions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["description"] == "Groceries"


def test_list_transactions_filters_combine_with_and(client):
    client.post("/api/transactions", json=_payload(category="Food", type="expense"))
    client.post("/api/transactions", json=_payload(category="Food", type="income", amount_cents=100))
    client.post("/api/transactions", json=_payload(category="Rent", type="expense"))

    response = client.get("/api/transactions", params={"category": "Food", "type": "expense"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "Food"
    assert body[0]["type"] == "expense"


def test_list_transactions_filters_by_date_range(client):
    client.post("/api/transactions", json=_payload(date="2025-01-01"))
    client.post("/api/transactions", json=_payload(date="2025-02-01"))
    client.post("/api/transactions", json=_payload(date="2025-03-01"))

    response = client.get(
        "/api/transactions", params={"start_date": "2025-01-15", "end_date": "2025-02-15"}
    )

    assert response.status_code == 200
    body = response.json()
    assert [t["date"] for t in body] == ["2025-02-01"]


def test_get_transaction_by_id(client):
    created = client.post("/api/transactions", json=_payload()).json()

    response = client.get(f"/api/transactions/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_transaction_returns_404(client):
    response = client.get("/api/transactions/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Transaction not found"}


def test_put_updates_transaction(client):
    created = client.post("/api/transactions", json=_payload()).json()

    response = client.put(
        f"/api/transactions/{created['id']}",
        json=_payload(description="Updated groceries", amount_cents=5000),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["description"] == "Updated groceries"
    assert body["amount_cents"] == 5000


def test_put_missing_transaction_returns_404(client):
    response = client.put("/api/transactions/999", json=_payload())

    assert response.status_code == 404


def test_delete_transaction_returns_204(client):
    created = client.post("/api/transactions", json=_payload()).json()

    response = client.delete(f"/api/transactions/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/transactions/{created['id']}").status_code == 404


def test_delete_missing_transaction_returns_404(client):
    response = client.delete("/api/transactions/999")

    assert response.status_code == 404


def test_invalid_type_returns_422(client):
    response = client.post("/api/transactions", json=_payload(type="transfer"))

    assert response.status_code == 422


def test_non_positive_amount_returns_422(client):
    response = client.post("/api/transactions", json=_payload(amount_cents=0))

    assert response.status_code == 422


def test_missing_required_field_returns_422(client):
    payload = _payload()
    del payload["description"]

    response = client.post("/api/transactions", json=payload)

    assert response.status_code == 422
