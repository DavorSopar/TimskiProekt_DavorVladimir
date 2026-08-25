"""Tests for CSV import (SCRUM-13, API_CONTRACT.md §5)."""

from app.database.models import Category, Transaction
from app.services.csv_import import import_csv

VALID_CSV = (
    "date,description,category,amount,type\n"
    "2025-01-15,Groceries,Food,42.50,expense\n"
    "2025-01-16,Paycheck,Income,2500.00,income\n"
)


def test_valid_rows_are_imported(db_session):
    result = import_csv(db_session, VALID_CSV)

    assert result == {"imported": 2, "skipped": 0, "errors": []}
    transactions = db_session.query(Transaction).order_by(Transaction.id).all()
    assert transactions[0].amount_cents == 4250
    assert transactions[0].type == "expense"
    assert transactions[1].amount_cents == 250000
    assert transactions[1].type == "income"


def test_unknown_categories_are_auto_created(db_session):
    import_csv(db_session, VALID_CSV)

    names = {c.name for c in db_session.query(Category).all()}
    assert names == {"Food", "Income"}


def test_existing_category_is_not_duplicated(db_session):
    db_session.add(Category(name="Food"))
    db_session.commit()

    import_csv(db_session, VALID_CSV)

    food_categories = db_session.query(Category).filter(Category.name == "Food").all()
    assert len(food_categories) == 1


def test_valid_rows_persist_even_if_other_rows_fail(db_session):
    csv_content = (
        "date,description,category,amount,type\n"
        "2025-01-15,Groceries,Food,42.50,expense\n"
        "not-a-date,Bad row,Food,10.00,expense\n"
        "2025-01-17,Another good row,Food,5.00,expense\n"
    )

    result = import_csv(db_session, csv_content)

    assert result["imported"] == 2
    assert result["skipped"] == 1
    assert result["errors"] == [{"row": 2, "message": "invalid date: 'not-a-date' (expected YYYY-MM-DD)"}]
    assert db_session.query(Transaction).count() == 2


def test_invalid_amount_is_rejected(db_session):
    csv_content = (
        "date,description,category,amount,type\n"
        "2025-01-15,Groceries,Food,not-a-number,expense\n"
    )

    result = import_csv(db_session, csv_content)

    assert result["imported"] == 0
    assert result["skipped"] == 1
    assert result["errors"][0]["row"] == 1


def test_non_positive_amount_is_rejected(db_session):
    csv_content = "date,description,category,amount,type\n2025-01-15,Groceries,Food,0,expense\n"

    result = import_csv(db_session, csv_content)

    assert result["skipped"] == 1


def test_invalid_type_is_rejected(db_session):
    csv_content = (
        "date,description,category,amount,type\n"
        "2025-01-15,Groceries,Food,10.00,Expense\n"  # capitalized: case-sensitive per contract
    )

    result = import_csv(db_session, csv_content)

    assert result["skipped"] == 1
    assert "invalid type" in result["errors"][0]["message"]


def test_wrong_header_is_rejected(db_session):
    csv_content = "when,what,category,amount,type\n2025-01-15,Groceries,Food,10.00,expense\n"

    result = import_csv(db_session, csv_content)

    assert result["imported"] == 0
    assert result["skipped"] == 0
    assert result["errors"][0]["row"] == 0
