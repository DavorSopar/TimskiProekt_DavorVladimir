"""Tests for the category API (SCRUM-09, API_CONTRACT.md §3)."""


def test_list_categories_empty_by_default(client):
    response = client.get("/api/categories")

    assert response.status_code == 200
    assert response.json() == []


def test_create_category_returns_201(client):
    response = client.post("/api/categories", json={"name": "Travel"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Travel"
    assert body["id"] is not None


def test_create_duplicate_category_returns_409(client):
    client.post("/api/categories", json={"name": "Travel"})

    response = client.post("/api/categories", json={"name": "Travel"})

    assert response.status_code == 409


def test_list_categories_after_create(client):
    client.post("/api/categories", json={"name": "Travel"})

    response = client.get("/api/categories")

    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert names == ["Travel"]


def test_delete_category_returns_204(client):
    created = client.post("/api/categories", json={"name": "Travel"}).json()

    response = client.delete(f"/api/categories/{created['id']}")

    assert response.status_code == 204
    assert client.get("/api/categories").json() == []


def test_delete_missing_category_returns_404(client):
    response = client.delete("/api/categories/999")

    assert response.status_code == 404


def test_delete_category_in_use_returns_409(client):
    created = client.post("/api/categories", json={"name": "Travel"}).json()
    client.post(
        "/api/transactions",
        json={
            "date": "2025-01-15",
            "description": "Flight",
            "category": "Travel",
            "amount_cents": 30000,
            "type": "expense",
        },
    )

    response = client.delete(f"/api/categories/{created['id']}")

    assert response.status_code == 409
