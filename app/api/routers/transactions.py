"""Transaction endpoints (API_CONTRACT.md §2)."""

from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import TransactionCreate, TransactionRead
from app.database import get_db
from app.services import transactions as transactions_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    return transactions_service.create_transaction(db, data)


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    category: str | None = None,
    type: str | None = None,
    start_date: date_type | None = None,
    end_date: date_type | None = None,
    db: Session = Depends(get_db),
):
    return transactions_service.list_transactions(
        db, category=category, type=type, start_date=start_date, end_date=end_date
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = transactions_service.get_transaction(db, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int, data: TransactionCreate, db: Session = Depends(get_db)
):
    transaction = transactions_service.update_transaction(db, transaction_id, data)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    deleted = transactions_service.delete_transaction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
