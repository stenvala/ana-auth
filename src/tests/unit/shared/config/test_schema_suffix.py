"""Tests for Config.SCHEMA_SUFFIX default."""

from shared.config import Config


def test_config_default_schema_suffix() -> None:
    """Config should default SCHEMA_SUFFIX to 'main'."""
    assert Config.SCHEMA_SUFFIX == "main"
