"""Tests for Config.get_database_url method."""

from shared.config import Config


def test_get_database_url_format() -> None:
    """get_database_url should return properly formatted PostgreSQL URL."""
    url = Config.get_database_url()
    assert "postgresql+psycopg2://" in url
    assert "localhost" in url
    assert "5432" in url
