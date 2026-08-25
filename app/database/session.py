"""SQLAlchemy engine and session configuration.

The database URL defaults to a local SQLite file under ``data/`` so the
app creates its own database on a fresh clone with no external database
server (see CLAUDE-PARTICIPANT-1.md, Database Rules). Set the
``DATABASE_URL`` environment variable to override it, e.g. for tests.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DEFAULT_DATABASE_URL = f"sqlite:///{(DATA_DIR / 'finance.db').as_posix()}"

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)

# SQLite needs this relaxed since a single connection may be used across
# threads (FastAPI's request handling); it does not apply to other backends.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

if DATABASE_URL.startswith("sqlite:///") and DATABASE_URL != "sqlite:///:memory:":
    DATA_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
