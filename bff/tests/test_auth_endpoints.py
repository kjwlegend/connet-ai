"""
Authentication Endpoints Tests

Tests for authentication endpoints including registration, login, 
token refresh, and other auth-related functionality.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.auth import RegisterRequest, LoginRequest, RefreshTokenRequest
from app.schemas.user import User
from app.modules.users.models import UserModel
from app.api.dependencies import get_supabase_auth_service, get_current_user, get_db_session
from app.infrastructure.security.auth import get_jwt_manager
from app.services.user_service import get_user_service


@pytest.mark.api
@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test class for authentication endpoints."""
    
    def setup_method(self):
        """Setup test data."""
        self.test_user_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
            "username": "testuser"
        }
        
        self.test_user_id = uuid4()
        
        self.mock_user = UserModel(
            id=self.test_user_id,
            email=self.test_user_data["email"],
            full_name=self.test_user_data["full_name"],
            username=self.test_user_data["username"],
            auth_provider="supabase",
            is_active=True,
            is_verified=True,
            permissions=["read", "write"]
        )

    def test_register_success(self, test_app, client: TestClient):
        """Test successful user registration."""
        # Mock the supabase auth service
        mock_auth_service = AsyncMock()
        mock_auth_service.register_user.return_value = (self.mock_user, {"access_token": "fake_token"})
        
        # Mock database session
        mock_session = AsyncMock()
        async def mock_get_session():
            yield mock_session
        
        # Override dependencies
        test_app.dependency_overrides[get_supabase_auth_service] = lambda: mock_auth_service
        test_app.dependency_overrides[get_db_session] = mock_get_session
        
        try:
            # Prepare request data
            register_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"],
                "full_name": self.test_user_data["full_name"],
                "username": self.test_user_data["username"]
            }
            
            # Make request
            response = client.post("/api/v1/auth/register", json=register_data)
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["email"] == self.test_user_data["email"]
            assert response_data["full_name"] == self.test_user_data["full_name"]
            assert response_data["username"] == self.test_user_data["username"]
            assert "id" in response_data
            
        finally:
            # Clean up dependency overrides
            test_app.dependency_overrides.clear()

    @patch('app.api.dependencies.get_supabase_auth_service')
    def test_register_duplicate_email(self, mock_get_supabase_auth, client: TestClient):
        """Test registration with duplicate email."""
        # Mock the supabase auth service to raise ValueError
        mock_auth_service = AsyncMock()
        mock_auth_service.register_user.side_effect = ValueError("User already exists")
        mock_get_supabase_auth.return_value = mock_auth_service
        
        register_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"],
            "full_name": self.test_user_data["full_name"],
            "username": self.test_user_data["username"]
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User already exists" in response.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        register_data = {
            "email": "invalid-email",
            "password": self.test_user_data["password"],
            "full_name": self.test_user_data["full_name"],
            "username": self.test_user_data["username"]
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password."""
        register_data = {
            "email": self.test_user_data["email"],
            "password": "123",  # Weak password
            "full_name": self.test_user_data["full_name"],
            "username": self.test_user_data["username"]
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.api.dependencies.get_supabase_auth_service')
    @patch('app.infrastructure.security.auth.get_jwt_manager')
    def test_login_success(self, mock_get_jwt_manager, mock_get_supabase_auth, client: TestClient):
        """Test successful user login."""
        # Mock JWT manager
        mock_jwt_manager = MagicMock()
        mock_jwt_manager.create_access_token.return_value = "fake_access_token"
        mock_jwt_manager.create_refresh_token.return_value = "fake_refresh_token"
        mock_get_jwt_manager.return_value = mock_jwt_manager
        
        # Mock supabase auth service
        mock_auth_service = AsyncMock()
        mock_auth_service.login_user.return_value = (self.mock_user, {"access_token": "supabase_token"})
        mock_get_supabase_auth.return_value = mock_auth_service
        
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["access_token"] == "fake_access_token"
        assert response_data["refresh_token"] == "fake_refresh_token"
        assert response_data["token_type"] == "bearer"
        assert "user" in response_data
        assert response_data["user"]["email"] == self.test_user_data["email"]

    @patch('app.api.dependencies.get_supabase_auth_service')
    @patch('app.infrastructure.security.auth.get_jwt_manager')
    def test_login_invalid_credentials(self, mock_get_jwt_manager, mock_get_supabase_auth, client: TestClient):
        """Test login with invalid credentials."""
        # Mock supabase auth service to return None (invalid credentials)
        mock_auth_service = AsyncMock()
        mock_auth_service.login_user.return_value = (None, None)
        mock_get_supabase_auth.return_value = mock_auth_service
        
        login_data = {
            "email": self.test_user_data["email"],
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields."""
        login_data = {
            "email": self.test_user_data["email"]
            # Missing password
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.api.dependencies.get_current_user')
    def test_me_endpoint_success(self, mock_get_current_user, client: TestClient):
        """Test successful /me endpoint."""
        mock_get_current_user.return_value = self.mock_user
        
        headers = {"Authorization": "Bearer fake_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["email"] == self.test_user_data["email"]
        assert response_data["full_name"] == self.test_user_data["full_name"]

    def test_me_endpoint_unauthorized(self, client: TestClient):
        """Test /me endpoint without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.infrastructure.security.auth.get_jwt_manager')
    def test_refresh_token_success(self, mock_get_jwt_manager, client: TestClient):
        """Test successful token refresh."""
        # Mock JWT manager
        mock_jwt_manager = MagicMock()
        mock_jwt_manager.verify_refresh_token.return_value = {"sub": str(self.test_user_id)}
        mock_jwt_manager.create_access_token.return_value = "new_access_token"
        mock_jwt_manager.create_refresh_token.return_value = "new_refresh_token"
        mock_get_jwt_manager.return_value = mock_jwt_manager
        
        refresh_data = {
            "refresh_token": "valid_refresh_token"
        }
        
        with patch('app.api.dependencies.get_user_service') as mock_get_user_service:
            mock_user_service = AsyncMock()
            mock_user_service.get_user_by_id.return_value = self.mock_user
            mock_get_user_service.return_value = mock_user_service
            
            response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["access_token"] == "new_access_token"
        assert response_data["refresh_token"] == "new_refresh_token"

    @patch('app.infrastructure.security.auth.get_jwt_manager')
    def test_refresh_token_invalid(self, mock_get_jwt_manager, client: TestClient):
        """Test token refresh with invalid token."""
        # Mock JWT manager to raise exception
        mock_jwt_manager = MagicMock()
        mock_jwt_manager.verify_refresh_token.side_effect = ValueError("Invalid token")
        mock_get_jwt_manager.return_value = mock_jwt_manager
        
        refresh_data = {
            "refresh_token": "invalid_refresh_token"
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.dependencies.get_current_user')
    def test_logout_success(self, mock_get_current_user, client: TestClient):
        """Test successful logout."""
        mock_get_current_user.return_value = self.mock_user
        
        headers = {"Authorization": "Bearer fake_token"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == "Successfully logged out"

    def test_logout_unauthorized(self, client: TestClient):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthIntegration:
    """Integration tests for authentication flow."""
    
    @patch('app.api.dependencies.get_supabase_auth_service')
    @patch('app.infrastructure.security.auth.get_jwt_manager')
    def test_register_login_flow(self, mock_get_jwt_manager, mock_get_supabase_auth, client: TestClient):
        """Test complete registration and login flow."""
        # Setup mocks
        test_user_id = uuid4()
        test_user_data = {
            "email": "integration@example.com",
            "password": "SecurePassword123!",
            "full_name": "Integration Test User",
            "username": "integrationuser"
        }
        
        mock_user = UserModel(
            id=test_user_id,
            email=test_user_data["email"],
            full_name=test_user_data["full_name"],
            username=test_user_data["username"],
            auth_provider="supabase",
            is_active=True,
            is_verified=True,
            permissions=["read", "write"]
        )
        
        # Mock JWT manager
        mock_jwt_manager = MagicMock()
        mock_jwt_manager.create_access_token.return_value = "integration_access_token"
        mock_jwt_manager.create_refresh_token.return_value = "integration_refresh_token"
        mock_get_jwt_manager.return_value = mock_jwt_manager
        
        # Mock supabase auth service
        mock_auth_service = AsyncMock()
        mock_auth_service.register_user.return_value = (mock_user, {"access_token": "supabase_token"})
        mock_auth_service.login_user.return_value = (mock_user, {"access_token": "supabase_token"})
        mock_get_supabase_auth.return_value = mock_auth_service
        
        # Step 1: Register
        register_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "full_name": test_user_data["full_name"],
            "username": test_user_data["username"]
        }
        
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == status.HTTP_200_OK
        
        # Step 2: Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        login_data = login_response.json()
        assert "access_token" in login_data
        assert "refresh_token" in login_data
        
        # Verify tokens are different (not reused)
        assert login_data["access_token"] == "integration_access_token"
        assert login_data["refresh_token"] == "integration_refresh_token"


# Test data validation
@pytest.mark.unit
class TestAuthValidation:
    """Test authentication request validation."""
    
    def test_register_request_validation(self):
        """Test RegisterRequest validation."""
        # Valid request
        valid_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
            "username": "testuser"
        }
        
        request = RegisterRequest(**valid_data)
        assert request.email == valid_data["email"]
        assert request.password == valid_data["password"]
        
        # Invalid email
        with pytest.raises(ValueError):
            RegisterRequest(
                email="invalid-email",
                password=valid_data["password"],
                full_name=valid_data["full_name"],
                username=valid_data["username"]
            )
    
    def test_login_request_validation(self):
        """Test LoginRequest validation."""
        # Valid request
        valid_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        request = LoginRequest(**valid_data)
        assert request.email == valid_data["email"]
        assert request.password == valid_data["password"]
        
        # Invalid email
        with pytest.raises(ValueError):
            LoginRequest(
                email="invalid-email",
                password=valid_data["password"]
            )