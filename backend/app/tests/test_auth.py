# tests/test_auth.py
import pytest
import uuid
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import app and models after path is set
from backend.app.models import user
from main import app
from app.core.database import Base, get_db
from app.models import *  # Import all models to ensure they're registered with Base.metadata
from app.tests.test_migrations import run_migrations
from app.core.database import async_engine as engine
from app.core.database import sync_engine as sync_engine

from app.core.database import Base
# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create the test database engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a TestingSessionLocal
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Setup function to create tables
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Run migrations to create tables
    run_migrations(sync_engine)
    yield
    # Drop all tables after tests are done
    Base.metadata.drop_all(bind=sync_engine)

# Create a test client
@pytest.fixture
def client():
    # Use the test client
    with TestClient(app) as c:
        yield c

# Test user registration with a unique user
def test_user_registration(client):
    # Generate a unique username/email to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@systemrebellion.com"
    
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "SecureP@ssw0rd123!"
        }
    )
    
    print(f"Registration response: {response.status_code}, {response.text}")
    
    # Should succeed with 200
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email
    assert "id" in data

# Test duplicate registration
def test_duplicate_registration(client):
    # First create a user
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@systemrebellion.com"
    
    # Register first time
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "SecureP@ssw0rd123!"
        }
    )
    assert response.status_code == 200
    
    # Try to register the same user again
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "SecureP@ssw0rd123!"
        }
    )
    
    print(f"Duplicate registration response: {response.status_code}, {response.text}")
    
    # Should fail with 400 (already registered)
    assert response.status_code == 400

# Test login with a newly registered user
def test_login(client):
    # First create a user
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@systemrebellion.com"
    
    # Register the user
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "SecureP@ssw0rd123!"
        }
    )
    assert response.status_code == 200
    
    # Now try to login
    response = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": "SecureP@ssw0rd123!"
        }
    )
    
    print(f"Login response: {response.status_code}, {response.text}")
    
    # Should succeed
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

# Test invalid login
def test_invalid_login(client):
    # First create a user
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@systemrebellion.com"
    
    # Register the user
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "SecureP@ssw0rd123!"
        }
    )
    assert response.status_code == 200
    
    # Try to login with wrong password
    response = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": "WrongPassword123!"
        }
    )
    
    print(f"Invalid login response: {response.status_code}, {response.text}")
    
    # Should fail with 401
    assert response.status_code == 401