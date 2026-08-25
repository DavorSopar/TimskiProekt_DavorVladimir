"""Category business logic and data access (API_CONTRACT.md §3)."""

from sqlalchemy.orm import Session

from app.database.models import Category, Transaction


class CategoryAlreadyExists(Exception):
    """Raised when creating a category whose name already exists."""


class CategoryInUse(Exception):
    """Raised when deleting a category still referenced by a transaction."""


def list_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.name).all()


def create_category(db: Session, name: str) -> Category:
    if db.query(Category).filter(Category.name == name).first() is not None:
        raise CategoryAlreadyExists(name)
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    category = db.get(Category, category_id)
    if category is None:
        return False
    in_use = db.query(Transaction).filter(Transaction.category == category.name).first()
    if in_use is not None:
        raise CategoryInUse(category.name)
    db.delete(category)
    db.commit()
    return True
