# tests/test_auth.py
from fastapi.testclient import TestClient
from main import create_application
from database import get_db
from models.user import User

client = TestClient(create_application())

def test_user_registration():
    # Sir Hawkington's Registration Validation
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@systemrebellion.com",
        "password": "SecureP@ssw0rd123!"
    })
    assert response.status_code == 200
    assert "id" in response.json()

def test_login():
    # The Meth Snail's Authentication Chaos
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "SecureP@ssw0rd123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_login():
    # Quantum Shadow People Denial Protocol
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "WrongPassword123!"
    })
    assert response.status_code == 401