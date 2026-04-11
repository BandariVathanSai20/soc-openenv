from fastapi.testclient import TestClient
from server.app import app
import pytest

# We use a context manager or explicit initialization to be clean
client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_reset_endpoint():
    response = client.post("/reset", json={"difficulty": "easy"})
    assert response.status_code == 200
    data = response.json()
    assert "observation" in data
    assert data["state"]["step"] == 0

def test_step_endpoint():
    # Ensure environment is reset before step
    client.post("/reset", json={"difficulty": "easy"})
    response = client.post("/step", json={"action": "normal"})
    assert response.status_code == 200
    data = response.json()
    assert "reward" in data
    assert "info" in data

def test_state_endpoint():
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert "step" in data