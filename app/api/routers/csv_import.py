"""CSV import endpoint (API_CONTRACT.md §5)."""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.schemas import ImportResult
from app.database import get_db
from app.services import csv_import as csv_import_service

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/csv", response_model=ImportResult)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8-sig")
    return csv_import_service.import_csv(db, content)
