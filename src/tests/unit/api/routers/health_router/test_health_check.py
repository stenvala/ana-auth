"""Tests for the health_check endpoint."""

from fastapi.testclient import TestClient

from api.main import app


def test_health_check_returns_200() -> None:
    """Health check should return 200 with status ok."""
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
