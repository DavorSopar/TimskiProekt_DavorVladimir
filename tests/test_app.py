"""Tests for the FastAPI app skeleton (SCRUM-05)."""

from fastapi.testclient import TestClient

from app.main import app


def test_app_is_a_fastapi_instance():
    assert app.title == "Personal Finance Tracker API"


def test_openapi_schema_generates_and_all_paths_are_under_api_prefix():
    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    for path in schema["paths"]:
        assert path.startswith("/api")


def test_docs_are_served():
    client = TestClient(app)
    response = client.get("/docs")

    assert response.status_code == 200
