"""Smoke test for the FIN-01 project scaffolding."""

import importlib


def test_app_packages_are_importable():
    for module in ("app", "app.api", "app.database", "app.services"):
        assert importlib.import_module(module) is not None


def test_core_dependencies_are_installed():
    for module in ("fastapi", "sqlalchemy"):
        assert importlib.import_module(module) is not None
