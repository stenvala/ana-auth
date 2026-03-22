"""Unit test conftest -- mock-oriented fixtures."""

from unittest.mock import MagicMock

import pytest
from sqlmodel import Session


@pytest.fixture()
def mock_session() -> MagicMock:
    """Provide a mocked SQLModel Session for unit tests."""
    return MagicMock(spec=Session)
