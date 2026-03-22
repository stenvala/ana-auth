"""Tests for DBContext.__init__ method."""

from shared.db.db_context import DBContext


def test_db_context_default_schema() -> None:
    """DBContext should default to Config.SCHEMA_SUFFIX."""
    ctx = DBContext()
    assert ctx.schema_suffix == "main"


def test_db_context_custom_schema() -> None:
    """DBContext should accept a custom schema suffix."""
    ctx = DBContext("e2e")
    assert ctx.schema_suffix == "e2e"
