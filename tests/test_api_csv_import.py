"""Tests for the CSV import API endpoint (SCRUM-13, API_CONTRACT.md §5)."""

VALID_CSV = (
    "date,description,category,amount,type\n"
    "2025-01-15,Groceries,Food,42.50,expense\n"
    "2025-01-16,Paycheck,Income,2500.00,income\n"
)


def test_import_csv_returns_200_with_summary(client):
    files = {"file": ("transactions.csv", VALID_CSV, "text/csv")}

    response = client.post("/api/import/csv", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["imported"] == 2
    assert body["skipped"] == 0
    assert body["errors"] == []


def test_imported_transactions_are_visible_via_the_transactions_api(client):
    files = {"file": ("transactions.csv", VALID_CSV, "text/csv")}
    client.post("/api/import/csv", files=files)

    response = client.get("/api/transactions")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_import_csv_reports_row_errors(client):
    csv_content = (
        "date,description,category,amount,type\n"
        "2025-01-15,Groceries,Food,42.50,expense\n"
        "bad,Bad row,Food,10.00,expense\n"
    )
    files = {"file": ("transactions.csv", csv_content, "text/csv")}

    response = client.post("/api/import/csv", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["imported"] == 1
    assert body["skipped"] == 1
    assert body["errors"][0]["row"] == 2
