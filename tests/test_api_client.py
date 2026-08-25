"""Tests for the Streamlit API client (SCRUM-06)."""

import requests

from app.streamlit import api_client


class _FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self.ok = status_code < 400
        self._payload = payload if payload is not None else []

    def json(self):
        return self._payload


def test_get_base_url_defaults_when_env_var_unset(monkeypatch):
    monkeypatch.delenv("FINANCE_API_URL", raising=False)
    assert api_client.get_base_url() == api_client.DEFAULT_BASE_URL


def test_get_base_url_reads_env_var(monkeypatch):
    monkeypatch.setenv("FINANCE_API_URL", "http://example.test:9000")
    assert api_client.get_base_url() == "http://example.test:9000"


def test_get_categories_returns_parsed_json(monkeypatch):
    seeded = [{"id": 1, "name": "Food"}, {"id": 2, "name": "Rent"}]

    def fake_get(url, timeout):
        assert url == f"{api_client.DEFAULT_BASE_URL}/api/categories"
        return _FakeResponse(200, seeded)

    monkeypatch.delenv("FINANCE_API_URL", raising=False)
    monkeypatch.setattr(api_client.requests, "get", fake_get)

    assert api_client.get_categories() == seeded


def test_get_categories_raises_api_error_on_connection_failure(monkeypatch):
    def fake_get(url, timeout):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr(api_client.requests, "get", fake_get)

    try:
        api_client.get_categories()
    except api_client.APIError:
        pass
    else:
        raise AssertionError("expected APIError to be raised")


def test_get_categories_raises_api_error_on_bad_status(monkeypatch):
    def fake_get(url, timeout):
        return _FakeResponse(500, {"detail": "boom"})

    monkeypatch.setattr(api_client.requests, "get", fake_get)

    try:
        api_client.get_categories()
    except api_client.APIError:
        pass
    else:
        raise AssertionError("expected APIError to be raised")
