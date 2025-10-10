"""
Simple Authentication Tests

Basic tests to verify authentication endpoints are accessible and working.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.api.dependencies import get_supabase_auth_service, get_db_session
from app.modules.users.models import UserModel
from uuid import uuid4


@pytest.fixture
def mock_dependencies(test_app):
    """Set up mock dependencies for testing."""
    # Create mock services
    mock_auth_service = AsyncMock()
    mock_session = AsyncMock()
    
    async def mock_get_session():
        yield mock_session
    
    # Override dependencies
    test_app.dependency_overrides[get_supabase_auth_service] = lambda: mock_auth_service
    test_app.dependency_overrides[get_db_session] = mock_get_session
    
    yield {
        "auth_service": mock_auth_service,
        "session": mock_session
    }
    
    # Clean up
    test_app.dependency_overrides.clear()


class TestAuthSimple:
    """Simple authentication endpoint tests."""
    
    def test_register_endpoint_exists(self, client: TestClient):
        """Test that register endpoint exists and accepts requests."""
        register_data = {
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User",
            "username": "testuser"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != status.HTTP_404_NOT_FOUND
        # Should not return 405 (method allowed)
        assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_login_endpoint_exists(self, client: TestClient):
        """Test that login endpoint exists and accepts requests."""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != status.HTTP_404_NOT_FOUND
        # Should not return 405 (method allowed)
        assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_me_endpoint_exists(self, client: TestClient):
        """Test that /me endpoint exists."""
        response = client.get("/api/v1/auth/me")
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != status.HTTP_404_NOT_FOUND
        # Should not return 405 (method allowed)
        assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_register_successful_with_mocks(self, client: TestClient, mock_dependencies):
        """Test successful registration with properly mocked dependencies."""
        # Set up mock return values
        mock_user = UserModel(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            username="testuser",
            auth_provider="supabase",
            is_active=True,
            is_verified=True
        )
        
        mock_dependencies["auth_service"].register_user.return_value = (
            mock_user, 
            {"access_token": "fake_token"}
        )
        
        register_data = {
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User",
            "username": "testuser"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        # Should succeed
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert response_data["email"] == "test@example.com"
        assert response_data["full_name"] == "Test User"
        assert response_data["username"] == "testuser"
    
    def test_login_endpoint_accepts_requests(self, client: TestClient, mock_dependencies):
        """Test that login endpoint accepts requests with mocked dependencies."""
        # Set up mock return values
        mock_user = UserModel(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            username="testuser",
            auth_provider="supabase",
            is_active=True,
            is_verified=True,
            permissions=["read", "write"]
        )
        
        mock_dependencies["auth_service"].login_user.return_value = (
            mock_user, 
            {"access_token": "supabase_token"}
        )
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Should not be a 404 or 405 error
        assert response.status_code not in [status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED]
    
    def test_register_validation_errors(self, client: TestClient):
        """Test registration input validation."""
        # Test missing required fields
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test invalid email format
        invalid_data = {
            "email": "not-an-email",
            "password": "Password123!",
            "full_name": "Test User",
            "username": "testuser"
        }
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_validation_errors(self, client: TestClient):
        """Test login input validation."""
        # Test missing required fields
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test invalid email format
        invalid_data = {
            "email": "not-an-email",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY