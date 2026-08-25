"""Tests for the shared money-formatting helpers (SCRUM-08)."""

from app.streamlit import formatting


def test_dollars_to_cents_converts_exactly():
    assert formatting.dollars_to_cents(42.50) == 4250


def test_dollars_to_cents_rounds_floating_point_noise():
    # 19.99 * 100 is 1998.9999999999998 in raw float math.
    assert formatting.dollars_to_cents(19.99) == 1999


def test_cents_to_dollars_converts_exactly():
    assert formatting.cents_to_dollars(4250) == 42.50


def test_format_cents_adds_dollar_sign_and_two_decimals():
    assert formatting.format_cents(4250) == "$42.50"


def test_format_cents_adds_thousands_separator():
    assert formatting.format_cents(250000) == "$2,500.00"


def test_format_cents_handles_zero():
    assert formatting.format_cents(0) == "$0.00"


def test_format_cents_handles_negative_amounts():
    assert formatting.format_cents(-5000) == "-$50.00"
