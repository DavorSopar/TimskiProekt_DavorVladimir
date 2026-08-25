"""Declarative base shared by all SQLAlchemy models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models (see app/database, models added per issue)."""
