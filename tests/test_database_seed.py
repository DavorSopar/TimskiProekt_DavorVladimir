"""Tests for the default category seed set (SCRUM-09, API_CONTRACT.md §3)."""

from app.database.models import Category
from app.database.seed import DEFAULT_CATEGORIES, seed_default_categories


def test_seed_inserts_default_categories_on_empty_table(db_session):
    seed_default_categories(db_session)

    names = {c.name for c in db_session.query(Category).all()}
    assert names == set(DEFAULT_CATEGORIES)


def test_seed_is_a_noop_if_categories_already_exist(db_session):
    db_session.add(Category(name="Custom"))
    db_session.commit()

    seed_default_categories(db_session)

    names = {c.name for c in db_session.query(Category).all()}
    assert names == {"Custom"}
