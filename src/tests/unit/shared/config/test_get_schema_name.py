"""Tests for Config.get_schema_name method."""

from shared.config import Config


def test_get_schema_name_with_main() -> None:
    """get_schema_name should format 'main' suffix correctly."""
    assert Config.get_schema_name("main") == "ana-auth-main"


def test_get_schema_name_with_e2e() -> None:
    """get_schema_name should format 'e2e' suffix correctly."""
    assert Config.get_schema_name("e2e") == "ana-auth-e2e"
