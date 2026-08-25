"""Tests for month-window arithmetic used by monthly-trend (SCRUM-15)."""

from datetime import date

from app.services.analytics import _last_n_months


def test_last_n_months_within_same_year():
    assert _last_n_months(3, today=date(2025, 3, 15)) == ["2025-01", "2025-02", "2025-03"]


def test_last_n_months_wraps_across_year_boundary():
    assert _last_n_months(3, today=date(2025, 1, 15)) == ["2024-11", "2024-12", "2025-01"]


def test_last_n_months_default_is_six():
    assert len(_last_n_months(6, today=date(2025, 6, 1))) == 6
