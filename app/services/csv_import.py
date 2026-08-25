"""CSV import: parsing, per-row validation, and persistence (API_CONTRACT.md §5).

Import is all-or-nothing per row, not for the whole file: valid rows are
persisted even if other rows fail validation. Do not trust imported data —
every field is re-validated here regardless of what the file claims.
"""

import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.database.models import Category, Transaction

EXPECTED_HEADER = ["date", "description", "category", "amount", "type"]


def _parse_row(row: dict) -> tuple[dict | None, str | None]:
    """Validate one CSV row. Returns (transaction_fields, None) or (None, error)."""
    raw_date = row.get("date")
    try:
        parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None, f"invalid date: {raw_date!r} (expected YYYY-MM-DD)"

    description = (row.get("description") or "").strip()
    if not description:
        return None, "description is required"

    category = (row.get("category") or "").strip()
    if not category:
        return None, "category is required"

    raw_amount = row.get("amount")
    try:
        amount = Decimal(raw_amount)
    except (InvalidOperation, TypeError):
        return None, f"invalid amount: {raw_amount!r}"
    if amount <= 0:
        return None, "amount must be positive"

    txn_type = row.get("type")
    if txn_type not in ("income", "expense"):
        return None, f"invalid type: {txn_type!r} (expected 'income' or 'expense')"

    amount_cents = int((amount * 100).to_integral_value())

    return {
        "date": parsed_date,
        "description": description,
        "category": category,
        "amount_cents": amount_cents,
        "type": txn_type,
    }, None


def import_csv(db: Session, file_content: str) -> dict:
    """Parse and persist a CSV file per the locked format in API_CONTRACT.md §5."""
    reader = csv.DictReader(io.StringIO(file_content))
    if reader.fieldnames != EXPECTED_HEADER:
        return {
            "imported": 0,
            "skipped": 0,
            "errors": [
                {
                    "row": 0,
                    "message": "CSV header must be exactly: " + ",".join(EXPECTED_HEADER),
                }
            ],
        }

    imported = 0
    skipped = 0
    errors: list[dict] = []
    known_categories = {c.name for c in db.query(Category).all()}

    for row_number, row in enumerate(reader, start=1):
        fields, error = _parse_row(row)
        if error is not None:
            skipped += 1
            errors.append({"row": row_number, "message": error})
            continue

        if fields["category"] not in known_categories:
            db.add(Category(name=fields["category"]))
            known_categories.add(fields["category"])

        db.add(Transaction(**fields))
        imported += 1

    db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors}
