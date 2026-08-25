"""Category endpoints (API_CONTRACT.md §3)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import CategoryCreate, CategoryRead
from app.database import get_db
from app.services import categories as categories_service
from app.services.categories import CategoryAlreadyExists, CategoryInUse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return categories_service.list_categories(db)


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    try:
        return categories_service.create_category(db, data.name)
    except CategoryAlreadyExists:
        raise HTTPException(status_code=409, detail="Category already exists")


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        deleted = categories_service.delete_category(db, category_id)
    except CategoryInUse:
        raise HTTPException(status_code=409, detail="Category is in use by a transaction")
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
