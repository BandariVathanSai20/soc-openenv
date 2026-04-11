"""
tests/test_api.py

Integration tests for the FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)


def test_health_endpoint():
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_reset_endpoint():
    """Test the /reset endpoint."""
    response = client.post("/reset", json={"difficulty": "easy"})
    assert response.status_code == 200
    data = response.json()
    assert "observation" in data
    assert data["state"]["step"] == 0


def test_step_endpoint():
    """Test the /step endpoint."""
    client.post("/reset", json={"difficulty": "easy"})
    response = client.post("/step", json={"action": "suspicious"})
    assert response.status_code == 200
    data = response.json()
    assert "reward" in data
    assert "state" in data


def test_state_endpoint():
    """Test the /state endpoint."""
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert "step" in data
    assert "difficulty" in data