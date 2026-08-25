"""Pure helper for the CSV Import page's result banner.

Kept separate from view code so this is easy to unit test without a
Streamlit runtime.
"""

from __future__ import annotations


def classify_import_result(imported: int, skipped: int) -> tuple[str, str]:
    """Return (level, message) describing an import result.

    level is "warning" whenever anything was skipped or nothing was
    found at all, and "success" only when every row imported cleanly.
    """
    if imported == 0 and skipped == 0:
        return "warning", "No rows found in the file."
    if skipped == 0:
        return "success", f"Imported {imported} row(s)."
    return "warning", f"Imported {imported} row(s). Skipped {skipped} row(s) — see errors below."
