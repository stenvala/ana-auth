"""Integration test for health check endpoint."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_health_check_returns_ok(test_client: "TestClient") -> None:
    """Health endpoint should return 200 with status ok."""
    response = test_client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
