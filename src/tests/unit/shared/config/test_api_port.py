"""Tests for Config.API_PORT default."""

from shared.config import Config


def test_config_default_api_port() -> None:
    """Config should default API_PORT to 6784."""
    assert Config.API_PORT == 6784
