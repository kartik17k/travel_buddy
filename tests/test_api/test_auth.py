"""Test cases for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.core.database import get_db, SessionLocal
from app.models.database import User as DBUser


def test_register_user(client):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data  # Should not return password


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    # Register first user
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Try to register with same email
    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"]


def test_login_user(client):
    """Test user login."""
    # First register a user
    user_data = {
        "email": "login@example.com",
        "password": "testpassword123",
        "full_name": "Login User"
    }
    client.post("/auth/register", json=user_data)
    
    # Now login
    login_data = {
        "email": "login@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user(client):
    """Test getting current user info."""
    # Register and login user
    user_data = {
        "email": "current@example.com",
        "password": "testpassword123",
        "full_name": "Current User"
    }
    client.post("/auth/register", json=user_data)
    
    login_response = client.post("/auth/login", json={
        "email": "current@example.com",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    
    # Get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]


def test_verify_token(client):
    """Test token verification."""
    # Register and login user
    user_data = {
        "email": "verify@example.com",
        "password": "testpassword123",
        "full_name": "Verify User"
    }
    client.post("/auth/register", json=user_data)
    
    login_response = client.post("/auth/login", json={
        "email": "verify@example.com",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    
    # Verify token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/verify-token", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["email"] == user_data["email"]


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/auth/me")
    assert response.status_code == 401 or response.status_code == 403


def test_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
