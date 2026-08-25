"""Tests for the CSV Import result-banner helper (SCRUM-21)."""

from app.streamlit.csv_import_helpers import classify_import_result


def test_all_rows_imported_is_success():
    level, message = classify_import_result(3, 0)
    assert level == "success"
    assert message == "Imported 3 row(s)."


def test_some_rows_skipped_is_warning():
    level, message = classify_import_result(2, 1)
    assert level == "warning"
    assert "Imported 2 row(s)" in message
    assert "Skipped 1 row(s)" in message


def test_empty_file_is_warning():
    level, message = classify_import_result(0, 0)
    assert level == "warning"
    assert message == "No rows found in the file."


def test_all_rows_skipped_is_warning():
    level, message = classify_import_result(0, 4)
    assert level == "warning"
    assert "Skipped 4 row(s)" in message
