"""
Unit tests for user authentication endpoints using pytest.

Tests cover registration, login, token refresh, and user profile retrieval.
Each endpoint is tested with one success case and three failure cases.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

from apps.users.models import User


# ==================== SIGNUP TESTS ====================

@pytest.mark.django_db
class TestSignupView:
    """Test suite for user registration endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('users:auth-signup')
    
    def test_signup_success(self, api_client, user_data):
        """Test successful user registration (Good case)."""
        response = api_client.post(self.url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['email'] == user_data['email']
        assert response.data['user']['name'] == user_data['name']
        
        # Verify user was created in database
        assert User.objects.filter(email=user_data['email']).exists()
    
    def test_signup_duplicate_email(self, api_client, user_data, user):
        """Test registration with duplicate email (Bad case 1)."""
        # Try to register with existing user's email
        user_data['email'] = user.email
        response = api_client.post(self.url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_signup_password_mismatch(self, api_client, user_data):
        """Test registration with mismatched passwords (Bad case 2)."""
        user_data['password_confirm'] = 'differentpassword'
        response = api_client.post(self.url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
    
    def test_signup_short_password(self, api_client, user_data):
        """Test registration with password shorter than 6 characters (Bad case 3)."""
        user_data['password'] = '12345'  # Only 5 characters
        user_data['password_confirm'] = '12345'
        response = api_client.post(self.url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data


# ==================== LOGIN TESTS ====================

@pytest.mark.django_db
class TestLoginView:
    """Test suite for user login endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('users:auth-login')
    
    def test_login_success(self, api_client, login_data):
        """Test successful user login (Good case)."""
        response = api_client.post(self.url, login_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['email'] == login_data['email']
    
    def test_login_invalid_password(self, api_client, login_data):
        """Test login with wrong password (Bad case 1)."""
        login_data['password'] = 'wrongpassword'
        response = api_client.post(self.url, login_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent email (Bad case 2)."""
        invalid_payload = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        response = api_client.post(self.url, invalid_payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data
    
    def test_login_inactive_user(self, api_client, user, login_data):
        """Test login with deactivated account (Bad case 3)."""
        # Deactivate user
        user.is_active = False
        user.save()
        
        response = api_client.post(self.url, login_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data


# ==================== ME (PROFILE) TESTS ====================

@pytest.mark.django_db
class TestMeView:
    """Test suite for current user profile endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('users:auth-me')
    
    def test_me_success(self, authenticated_client, user):
        """Test retrieving current user profile with authentication (Good case)."""
        response = authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['name'] == user.name
        assert 'id' in response.data
        assert 'created_at' in response.data
        assert 'invitation_privacy' in response.data
    
    def test_me_unauthenticated(self, api_client):
        """Test accessing profile without authentication (Bad case 1)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_me_invalid_token(self, api_client):
        """Test accessing profile with invalid token (Bad case 2)."""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_here')
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    


# ==================== TOKEN REFRESH TESTS ====================

@pytest.mark.django_db
class TestTokenRefreshView:
    """Test suite for JWT token refresh endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('users:token_refresh')
    
    def test_token_refresh_success(self, api_client, user):
        """Test successful token refresh (Good case)."""
        refresh = RefreshToken.for_user(user)
        response = api_client.post(
            self.url,
            {'refresh': str(refresh)},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert response.data['access'] is not None
    
    def test_token_refresh_invalid_token(self, api_client):
        """Test refresh with invalid token (Bad case 1)."""
        response = api_client.post(
            self.url,
            {'refresh': 'invalid_refresh_token'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_refresh_missing_token(self, api_client):
        """Test refresh without providing token (Bad case 2)."""
        response = api_client.post(self.url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_token_refresh_access_token_instead(self, api_client, user):
        """Test refresh with access token instead of refresh token (Bad case 3)."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response = api_client.post(
            self.url,
            {'refresh': access_token},
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
