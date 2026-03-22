"""Integration test conftest -- TestClient with schema injection."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient

from api.main import create_app


@pytest.fixture(scope="session")
def test_client(test_schema_suffix: str) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient with X-Schema header injection."""
    app = create_app()
    with TestClient(app) as client:
        client.headers.update({"X-Schema": test_schema_suffix})
        yield client
