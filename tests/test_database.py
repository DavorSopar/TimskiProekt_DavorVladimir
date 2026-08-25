"""Tests for SQLite + SQLAlchemy configuration (SCRUM-03)."""

from sqlalchemy import text

from app.database import DATABASE_URL, get_db, init_db


def test_database_url_defaults_to_local_sqlite_file():
    assert DATABASE_URL.startswith("sqlite:///")
    assert "finance.db" in DATABASE_URL


def test_get_db_yields_a_working_session():
    db_gen = get_db()
    db = next(db_gen)
    try:
        assert db.execute(text("SELECT 1")).scalar() == 1
    finally:
        db_gen.close()


def test_init_db_is_idempotent():
    init_db()
    init_db()
