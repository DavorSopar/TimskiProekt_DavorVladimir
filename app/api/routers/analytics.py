"""Analytics endpoints (API_CONTRACT.md §6)."""

from datetime import date as date_type

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import AnalyticsSummary, CategoryTotal, MonthlyTrend
from app.database import get_db
from app.services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    start_date: date_type | None = None,
    end_date: date_type | None = None,
    db: Session = Depends(get_db),
):
    return analytics_service.get_summary(db, start_date, end_date)


@router.get("/by-category", response_model=list[CategoryTotal])
def get_by_category(
    start_date: date_type | None = None,
    end_date: date_type | None = None,
    db: Session = Depends(get_db),
):
    return analytics_service.get_by_category(db, start_date, end_date)


@router.get("/monthly-trend", response_model=list[MonthlyTrend])
def get_monthly_trend(months: int = 6, db: Session = Depends(get_db)):
    return analytics_service.get_monthly_trend(db, months)
