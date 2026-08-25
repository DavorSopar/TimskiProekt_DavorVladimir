"""Tests for the Streamlit API client (SCRUM-06, SCRUM-08)."""

import requests

from app.streamlit import api_client


class _FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self.ok = status_code < 400
        self._payload = payload if payload is not None else []
        self.text = text

    def json(self):
        if self._payload is _NO_BODY:
            raise ValueError("no JSON body")
        return self._payload


_NO_BODY = object()


def _patch_request(monkeypatch, fake_request):
    monkeypatch.setattr(api_client.requests, "request", fake_request)


def test_get_base_url_defaults_when_env_var_unset(monkeypatch):
    monkeypatch.delenv("FINANCE_API_URL", raising=False)
    assert api_client.get_base_url() == api_client.DEFAULT_BASE_URL


def test_get_base_url_reads_env_var(monkeypatch):
    monkeypatch.setenv("FINANCE_API_URL", "http://example.test:9000")
    assert api_client.get_base_url() == "http://example.test:9000"


def test_get_categories_returns_parsed_json(monkeypatch):
    seeded = [{"id": 1, "name": "Food"}, {"id": 2, "name": "Rent"}]

    def fake_request(method, url, timeout):
        assert method == "GET"
        assert url == f"{api_client.DEFAULT_BASE_URL}/api/categories"
        return _FakeResponse(200, seeded)

    monkeypatch.delenv("FINANCE_API_URL", raising=False)
    _patch_request(monkeypatch, fake_request)

    assert api_client.get_categories() == seeded


def test_get_categories_raises_api_error_on_connection_failure(monkeypatch):
    def fake_request(method, url, timeout):
        raise requests.ConnectionError("refused")

    _patch_request(monkeypatch, fake_request)

    try:
        api_client.get_categories()
    except api_client.APIError:
        pass
    else:
        raise AssertionError("expected APIError to be raised")


def test_get_categories_raises_api_error_on_bad_status(monkeypatch):
    def fake_request(method, url, timeout):
        return _FakeResponse(500, {"detail": "boom"})

    _patch_request(monkeypatch, fake_request)

    try:
        api_client.get_categories()
    except api_client.APIError as exc:
        assert "boom" in str(exc)
    else:
        raise AssertionError("expected APIError to be raised")


def test_error_detail_handles_string_detail(monkeypatch):
    def fake_request(method, url, timeout, **kwargs):
        return _FakeResponse(409, {"detail": "category already exists"})

    _patch_request(monkeypatch, fake_request)

    try:
        api_client.get_categories()
    except api_client.APIError as exc:
        assert str(exc) == "category already exists"
    else:
        raise AssertionError("expected APIError to be raised")


def test_error_detail_handles_validation_error_list(monkeypatch):
    def fake_request(method, url, timeout, **kwargs):
        payload = {
            "detail": [
                {"loc": ["body", "amount_cents"], "msg": "must be positive", "type": "value_error"}
            ]
        }
        return _FakeResponse(422, payload)

    _patch_request(monkeypatch, fake_request)

    try:
        api_client.get_categories()
    except api_client.APIError as exc:
        assert "amount_cents" in str(exc)
        assert "must be positive" in str(exc)
    else:
        raise AssertionError("expected APIError to be raised")


def test_error_detail_handles_non_json_body(monkeypatch):
    def fake_request(method, url, timeout, **kwargs):
        return _FakeResponse(500, _NO_BODY, text="internal server error")

    _patch_request(monkeypatch, fake_request)

    try:
        api_client.get_categories()
    except api_client.APIError as exc:
        assert "internal server error" in str(exc)
    else:
        raise AssertionError("expected APIError to be raised")


def test_list_transactions_sends_only_provided_filters(monkeypatch):
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured["params"] = kwargs.get("params")
        return _FakeResponse(200, [])

    _patch_request(monkeypatch, fake_request)

    api_client.list_transactions(category="Food", type_=None, start_date=None, end_date=None)

    assert captured["method"] == "GET"
    assert captured["url"].endswith("/api/transactions")
    assert captured["params"] == {"category": "Food"}


def test_create_transaction_posts_expected_body(monkeypatch):
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["method"] = method
        captured["json"] = kwargs.get("json")
        return _FakeResponse(201, {"id": 1, **kwargs["json"]})

    _patch_request(monkeypatch, fake_request)

    result = api_client.create_transaction(
        date="2025-01-15",
        description="Groceries",
        category="Food",
        amount_cents=4250,
        type_="expense",
    )

    assert captured["method"] == "POST"
    assert captured["json"] == {
        "date": "2025-01-15",
        "description": "Groceries",
        "category": "Food",
        "amount_cents": 4250,
        "type": "expense",
    }
    assert result["id"] == 1


def test_update_transaction_puts_to_correct_url(monkeypatch):
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["method"] = method
        captured["url"] = url
        return _FakeResponse(200, {"id": 7})

    _patch_request(monkeypatch, fake_request)

    api_client.update_transaction(
        7,
        date="2025-01-16",
        description="Paycheck",
        category="Income",
        amount_cents=250000,
        type_="income",
    )

    assert captured["method"] == "PUT"
    assert captured["url"].endswith("/api/transactions/7")


def test_delete_transaction_sends_delete(monkeypatch):
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["method"] = method
        captured["url"] = url
        return _FakeResponse(204, _NO_BODY)

    _patch_request(monkeypatch, fake_request)

    api_client.delete_transaction(7)

    assert captured["method"] == "DELETE"
    assert captured["url"].endswith("/api/transactions/7")


def test_list_budgets_omits_month_param_when_not_given(monkeypatch):
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured["params"] = kwargs.get("params")
        return _FakeResponse(200, [])

    _patch_request(monkeypatch, fake_request)

    api_client.list_budgets()

    assert captured["method"] == "GET"
    assert captured["url"].endswith("/api/budgets")
    assert captured["params"] == {}


def test_list_budgets_sends_month_param(monkeypatch):
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["params"] = kwargs.get("params")
        return _FakeResponse(200, [])

    _patch_request(monkeypatch, fake_request)

    api_client.list_budgets(month="2025-01")

    assert captured["params"] == {"month": "2025-01"}


def test_create_budget_posts_expected_body(monkeypatch):
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["method"] = method
        captured["json"] = kwargs.get("json")
        return _FakeResponse(201, {"id": 1, **kwargs["json"]})

    _patch_request(monkeypatch, fake_request)

    result = api_client.create_budget(category="Food", month="2025-01", amount_cents=20000)

    assert captured["method"] == "POST"
    assert captured["json"] == {"category": "Food", "month": "2025-01", "amount_cents": 20000}
    assert result["id"] == 1


def test_create_budget_raises_api_error_on_conflict(monkeypatch):
    def fake_request(method, url, timeout, **kwargs):
        return _FakeResponse(409, {"detail": "budget already exists"})

    _patch_request(monkeypatch, fake_request)

    try:
        api_client.create_budget(category="Food", month="2025-01", amount_cents=20000)
    except api_client.APIError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("expected APIError to be raised")


def test_update_budget_puts_amount_only(monkeypatch):
    captured = {}

    def fake_request(method, url, timeout, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured["json"] = kwargs.get("json")
        return _FakeResponse(200, {"id": 1, "amount_cents": 30000})

    _patch_request(monkeypatch, fake_request)

    api_client.update_budget(1, amount_cents=30000)

    assert captured["method"] == "PUT"
    assert captured["url"].endswith("/api/budgets/1")
    assert captured["json"] == {"amount_cents": 30000}


def test_get_budget_status_returns_parsed_json(monkeypatch):
    payload = {
        "budget": {"id": 1, "category": "Food", "month": "2025-01", "amount_cents": 20000},
        "spent_cents": 5000,
        "remaining_cents": 15000,
        "over_budget": False,
    }

    def fake_request(method, url, timeout, **kwargs):
        assert url.endswith("/api/budgets/1/status")
        return _FakeResponse(200, payload)

    _patch_request(monkeypatch, fake_request)

    assert api_client.get_budget_status(1) == payload
