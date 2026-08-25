"""Transaction business logic and data access (API_CONTRACT.md §2)."""

from datetime import date as date_type

from sqlalchemy.orm import Session

from app.api.schemas import TransactionCreate
from app.database.models import Transaction


def create_transaction(db: Session, data: TransactionCreate) -> Transaction:
    transaction = Transaction(**data.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def list_transactions(
    db: Session,
    category: str | None = None,
    type: str | None = None,
    start_date: date_type | None = None,
    end_date: date_type | None = None,
) -> list[Transaction]:
    query = db.query(Transaction)
    if category is not None:
        query = query.filter(Transaction.category == category)
    if type is not None:
        query = query.filter(Transaction.type == type)
    if start_date is not None:
        query = query.filter(Transaction.date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.date <= end_date)
    return query.order_by(Transaction.date, Transaction.id).all()


def get_transaction(db: Session, transaction_id: int) -> Transaction | None:
    return db.get(Transaction, transaction_id)


def update_transaction(
    db: Session, transaction_id: int, data: TransactionCreate
) -> Transaction | None:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        return None
    for field, value in data.model_dump().items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction_id: int) -> bool:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        return False
    db.delete(transaction)
    db.commit()
    return True
