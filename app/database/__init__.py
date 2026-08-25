"""SQLAlchemy engine, session, models and data access.

Engine/session configuration lives in ``app.database.session``; the shared
declarative base lives in ``app.database.base``; ORM models live in
``app.database.models``. Import models here so they register on ``Base``
before ``init_db()`` is called.
"""

from app.database.base import Base
from app.database.models import Transaction
from app.database.session import DATABASE_URL, SessionLocal, engine, get_db

__all__ = [
    "Base",
    "DATABASE_URL",
    "SessionLocal",
    "engine",
    "get_db",
    "init_db",
    "Transaction",
]


def init_db() -> None:
    """Create all tables registered on ``Base``. Safe to call repeatedly."""
    Base.metadata.create_all(bind=engine)
