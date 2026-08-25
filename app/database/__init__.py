"""SQLAlchemy engine, session, models and data access.

Engine/session configuration lives in ``app.database.session``; the shared
declarative base lives in ``app.database.base``; ORM models live in
``app.database.models``. Import models here so they register on ``Base``
before ``init_db()`` is called.
"""

from app.database.base import Base
from app.database.models import Category, Transaction
from app.database.seed import seed_default_categories
from app.database.session import DATABASE_URL, SessionLocal, engine, get_db

__all__ = [
    "Base",
    "DATABASE_URL",
    "SessionLocal",
    "engine",
    "get_db",
    "init_db",
    "Category",
    "Transaction",
]


def init_db() -> None:
    """Create all tables and insert default seed data. Safe to call repeatedly."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()
