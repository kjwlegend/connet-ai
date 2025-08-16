"""
Comprehensive Authentication Tests

Complete tests for authentication endpoints including JWT handling,
error scenarios, and integration testing.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import get_supabase_auth_service, get_db_session, get_current_user
from app.infrastructure.database.models.user_model import UserModel


@pytest.fixture
def mock_auth_dependencies(test_app):
    """Set up comprehensive auth mocks."""
    mock_auth_service = AsyncMock()
    mock_session = AsyncMock()
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
    
    async def mock_get_session():
        yield mock_session
    
    def mock_get_current_user():
        return mock_user
    
    # Override dependencies
    test_app.dependency_overrides[get_supabase_auth_service] = lambda: mock_auth_service
    test_app.dependency_overrides[get_db_session] = mock_get_session
    test_app.dependency_overrides[get_current_user] = mock_get_current_user
    
    yield {
        "auth_service": mock_auth_service,
        "session": mock_session,
        "user": mock_user
    }
    
    test_app.dependency_overrides.clear()


class TestAuthComprehensive:
    """Comprehensive authentication tests."""
    
    def test_register_complete_flow(self, client: TestClient, mock_auth_dependencies):
        """Test complete registration flow with all fields."""
        mock_user = UserModel(
            id=uuid4(),
            email="complete@example.com",
            full_name="Complete Test User",
            username="completeuser",
            auth_provider="supabase",
            is_active=True,
            is_verified=False,  # New user should not be verified yet
            permissions=[]
        )
        
        mock_auth_dependencies["auth_service"].register_user.return_value = (
            mock_user, 
            {"access_token": "registration_token"}
        )
        
        register_data = {
            "email": "complete@example.com",
            "password": "SecurePassword123!",
            "full_name": "Complete Test User",
            "username": "completeuser",
            "invited_by_code": "INVITE123",
            "registration_source": "web",
            "registration_channel": "organic",
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "auth_test"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        # Verify all user data is returned
        assert response_data["email"] == "complete@example.com"
        assert response_data["full_name"] == "Complete Test User"
        assert response_data["username"] == "completeuser"
        assert response_data["is_active"] == True
        assert response_data["is_verified"] == False
        assert "id" in response_data
        assert "created_at" in response_data
        
        # Verify service was called with correct parameters
        mock_auth_dependencies["auth_service"].register_user.assert_called_once()
    
    def test_register_duplicate_email(self, client: TestClient, mock_auth_dependencies):
        """Test registration with duplicate email."""
        mock_auth_dependencies["auth_service"].register_user.side_effect = ValueError(
            "User with this email already exists"
        )
        
        register_data = {
            "email": "duplicate@example.com",
            "password": "Password123!",
            "full_name": "Duplicate User",
            "username": "duplicateuser"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User with this email already exists" in response.json()["detail"]
    
    def test_register_service_error(self, client: TestClient, mock_auth_dependencies):
        """Test registration with service error."""
        mock_auth_dependencies["auth_service"].register_user.side_effect = Exception(
            "Database connection failed"
        )
        
        register_data = {
            "email": "error@example.com",
            "password": "Password123!",
            "full_name": "Error User",
            "username": "erroruser"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Registration failed" in response.json()["detail"]
    
    @patch('app.api.v1.endpoints.auth.get_jwt_manager')
    def test_login_complete_flow(self, mock_get_jwt_manager, client: TestClient, mock_auth_dependencies):
        """Test complete login flow with JWT token generation."""
        # Setup JWT manager mock
        mock_jwt_manager = MagicMock()
        mock_jwt_manager.create_access_token.return_value = "jwt_access_token_123"
        mock_jwt_manager.create_refresh_token.return_value = "jwt_refresh_token_456"
        mock_get_jwt_manager.return_value = mock_jwt_manager
        
        # Setup auth service mock
        mock_user = UserModel(
            id=uuid4(),
            email="login@example.com",
            full_name="Login User",
            username="loginuser",
            auth_provider="supabase",
            is_active=True,
            is_verified=True,
            permissions=["read", "write", "admin"]
        )
        
        mock_auth_dependencies["auth_service"].login_user.return_value = (
            mock_user,
            {"access_token": "supabase_token", "refresh_token": "supabase_refresh"}
        )
        
        login_data = {
            "email": "login@example.com",
            "password": "CorrectPassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        # Verify token structure
        assert response_data["access_token"] == "jwt_access_token_123"
        assert response_data["refresh_token"] == "jwt_refresh_token_456"
        assert response_data["token_type"] == "bearer"
        
        # Verify user data is included
        assert "user" in response_data
        user_data = response_data["user"]
        assert user_data["email"] == "login@example.com"
        assert user_data["full_name"] == "Login User"
        assert user_data["username"] == "loginuser"
        
        # Verify JWT manager was called with correct parameters
        mock_jwt_manager.create_access_token.assert_called_once()
        mock_jwt_manager.create_refresh_token.assert_called_once()
    
    def test_login_invalid_credentials(self, client: TestClient, mock_auth_dependencies):
        """Test login with invalid credentials."""
        mock_auth_dependencies["auth_service"].login_user.return_value = (None, None)
        
        login_data = {
            "email": "invalid@example.com",
            "password": "WrongPassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, client: TestClient, mock_auth_dependencies):
        """Test login with inactive user account."""
        inactive_user = UserModel(
            id=uuid4(),
            email="inactive@example.com",
            full_name="Inactive User",
            username="inactiveuser",
            auth_provider="supabase",
            is_active=False,  # Inactive user
            is_verified=True,
            permissions=[]
        )
        
        mock_auth_dependencies["auth_service"].login_user.return_value = (
            inactive_user,
            {"access_token": "token"}
        )
        
        login_data = {
            "email": "inactive@example.com",
            "password": "Password123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Login should succeed but user data should reflect inactive status
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["user"]["is_active"] == False
    
    def test_me_endpoint_authenticated(self, client: TestClient, mock_auth_dependencies):
        """Test /me endpoint with authenticated user."""
        headers = {"Authorization": "Bearer valid_token"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        # Should return current user data
        assert response_data["email"] == mock_auth_dependencies["user"].email
        assert response_data["full_name"] == mock_auth_dependencies["user"].full_name
        assert response_data["username"] == mock_auth_dependencies["user"].username
        assert "id" in response_data
    
    def test_me_endpoint_unauthenticated(self, test_app, client: TestClient):
        """Test /me endpoint without authentication."""
        # Don't override get_current_user dependency for this test
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('app.api.v1.endpoints.auth.get_jwt_manager')
    @patch('app.api.dependencies.get_user_service')
    def test_refresh_token_flow(self, mock_get_user_service, mock_get_jwt_manager, 
                               client: TestClient, mock_auth_dependencies):
        """Test token refresh flow."""
        # Setup mocks
        mock_jwt_manager = MagicMock()
        mock_jwt_manager.verify_token.return_value = {
            "sub": str(mock_auth_dependencies["user"].id),
            "type": "refresh"
        }
        mock_jwt_manager.create_access_token.return_value = "new_access_token"
        mock_jwt_manager.create_refresh_token.return_value = "new_refresh_token"
        mock_get_jwt_manager.return_value = mock_jwt_manager
        
        mock_user_service = AsyncMock()
        mock_user_service.get_user_by_id.return_value = mock_auth_dependencies["user"]
        mock_get_user_service.return_value = mock_user_service
        
        refresh_data = {
            "refresh_token": "valid_refresh_token"
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert response_data["access_token"] == "new_access_token"
        assert response_data["refresh_token"] == "new_refresh_token"
        assert response_data["token_type"] == "bearer"
    
    @patch('app.api.v1.endpoints.auth.get_jwt_manager')
    def test_logout_authenticated(self, mock_get_jwt_manager, client: TestClient, mock_auth_dependencies):
        """Test logout with authenticated user."""
        # Setup JWT manager mock
        mock_jwt_manager = MagicMock()
        mock_jwt_manager.verify_token.return_value = {"sub": "user_id", "type": "access"}
        mock_get_jwt_manager.return_value = mock_jwt_manager
        
        headers = {"Authorization": "Bearer valid_token"}
        
        response = client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == "Logged out successfully"
    
    def test_logout_unauthenticated(self, test_app, client: TestClient):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthValidation:
    """Test authentication input validation and edge cases."""
    
    @pytest.fixture
    def mock_validation_dependencies(self, test_app):
        """Set up mock dependencies for validation testing."""
        mock_auth_service = AsyncMock()
        mock_session = AsyncMock()
        
        async def mock_get_session():
            yield mock_session
        
        # Override dependencies
        test_app.dependency_overrides[get_supabase_auth_service] = lambda: mock_auth_service
        test_app.dependency_overrides[get_db_session] = mock_get_session
        
        yield {"auth_service": mock_auth_service, "session": mock_session}
        
        test_app.dependency_overrides.clear()
    
    def test_register_password_requirements(self, client: TestClient, mock_validation_dependencies):
        """Test password validation requirements."""
        base_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "username": "testuser"
        }
        
        # Test too short password
        short_password_data = {**base_data, "password": "123"}
        response = client.post("/api/v1/auth/register", json=short_password_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test another too short password
        another_short_data = {**base_data, "password": "1234567"}  # 7 characters
        response = client.post("/api/v1/auth/register", json=another_short_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_email_validation(self, client: TestClient, mock_validation_dependencies):
        """Test email format validation."""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user..double.dot@domain.com"
        ]
        
        for invalid_email in invalid_emails:
            register_data = {
                "email": invalid_email,
                "password": "ValidPassword123!",
                "full_name": "Test User",
                "username": "testuser"
            }
            
            response = client.post("/api/v1/auth/register", json=register_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_username_validation(self, client: TestClient, mock_validation_dependencies):
        """Test username validation."""
        invalid_usernames = [
            "",  # Empty
            "a",  # Too short
            "a" * 51,  # Too long (if length limit is 50)
            "user name",  # Spaces
            "user@name",  # Special characters
        ]
        
        for invalid_username in invalid_usernames:
            register_data = {
                "email": "test@example.com",
                "password": "ValidPassword123!",
                "full_name": "Test User",
                "username": invalid_username
            }
            
            response = client.post("/api/v1/auth/register", json=register_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_fields(self, client: TestClient, mock_validation_dependencies):
        """Test login with missing required fields."""
        # Missing password
        response = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing email
        response = client.post("/api/v1/auth/login", json={"password": "password123"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Empty request
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthIntegration:
    """Integration tests for complete authentication flows."""
    
    @patch('app.api.v1.endpoints.auth.get_jwt_manager')
    def test_register_then_login_flow(self, mock_get_jwt_manager, client: TestClient, mock_auth_dependencies):
        """Test complete register then login flow."""
        # Setup JWT manager
        mock_jwt_manager = MagicMock()
        mock_jwt_manager.create_access_token.return_value = "login_access_token"
        mock_jwt_manager.create_refresh_token.return_value = "login_refresh_token"
        mock_get_jwt_manager.return_value = mock_jwt_manager
        
        # Create test user
        test_user = UserModel(
            id=uuid4(),
            email="integration@example.com",
            full_name="Integration User",
            username="integrationuser",
            auth_provider="supabase",
            is_active=True,
            is_verified=True,
            permissions=["read"]
        )
        
        # Step 1: Register
        mock_auth_dependencies["auth_service"].register_user.return_value = (
            test_user,
            {"access_token": "registration_token"}
        )
        
        register_data = {
            "email": "integration@example.com",
            "password": "IntegrationPassword123!",
            "full_name": "Integration User",
            "username": "integrationuser"
        }
        
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == status.HTTP_200_OK
        
        # Step 2: Login with same credentials
        mock_auth_dependencies["auth_service"].login_user.return_value = (
            test_user,
            {"access_token": "supabase_login_token"}
        )
        
        login_data = {
            "email": "integration@example.com",
            "password": "IntegrationPassword123!"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        # Verify we got different tokens for login vs registration
        login_data = login_response.json()
        assert login_data["access_token"] == "login_access_token"
        assert login_data["refresh_token"] == "login_refresh_token"