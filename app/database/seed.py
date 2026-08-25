"""Default seed data inserted on first DB creation (API_CONTRACT.md §3)."""

from sqlalchemy.orm import Session

from app.database.models import Category

DEFAULT_CATEGORIES = ["Food", "Rent", "Transport", "Utilities", "Income", "Other"]


def seed_default_categories(db: Session) -> None:
    """Insert the default category set only if categories don't exist yet."""
    if db.query(Category).first() is not None:
        return
    db.add_all(Category(name=name) for name in DEFAULT_CATEGORIES)
    db.commit()
