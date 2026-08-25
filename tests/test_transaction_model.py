"""Tests for the Transaction model (SCRUM-04).

Uses an isolated in-memory SQLite database per test so these stay
deterministic and independent of the app's configured data/finance.db.
"""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base, Transaction


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _make_transaction(**overrides):
    fields = {
        "date": date(2025, 1, 15),
        "description": "Groceries",
        "category": "Food",
        "amount_cents": 4250,
        "type": "expense",
    }
    fields.update(overrides)
    return Transaction(**fields)


def test_create_and_read_transaction(session):
    session.add(_make_transaction())
    session.commit()

    saved = session.query(Transaction).one()
    assert saved.id is not None
    assert saved.date == date(2025, 1, 15)
    assert saved.description == "Groceries"
    assert saved.category == "Food"
    assert saved.amount_cents == 4250
    assert saved.type == "expense"
    assert saved.created_at is not None


def test_income_type_is_accepted(session):
    session.add(_make_transaction(type="income", amount_cents=250000))
    session.commit()

    saved = session.query(Transaction).one()
    assert saved.type == "income"


def test_invalid_type_is_rejected(session):
    session.add(_make_transaction(type="transfer"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_non_positive_amount_is_rejected(session):
    session.add(_make_transaction(amount_cents=0))
    with pytest.raises(IntegrityError):
        session.commit()
