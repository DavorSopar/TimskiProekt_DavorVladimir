"""SQLAlchemy engine, session, models and data access.

Engine/session configuration lives in ``app.database.session``; the shared
declarative base lives in ``app.database.base``. Models are added per issue
(see SCRUM-04) under this package.
"""

from app.database.base import Base
from app.database.session import DATABASE_URL, SessionLocal, engine, get_db

__all__ = ["Base", "DATABASE_URL", "SessionLocal", "engine", "get_db", "init_db"]


def init_db() -> None:
    """Create all tables registered on ``Base``.

    No-op until models exist (SCRUM-04). Safe to call repeatedly.
    """
    Base.metadata.create_all(bind=engine)
