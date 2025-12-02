"""
Pytest configuration and fixtures for the entire project.
"""

import pytest
from rest_framework.test import APIClient
from apps.users.models import User


@pytest.fixture
def api_client():
    """
    Fixture that provides a DRF APIClient instance for making API requests.
    
    Returns:
        APIClient: Unauthenticated API client.
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Fixture that creates a test user in the database.
    
    Returns:
        User: A test user with email and password.
    """
    return User.objects.create_user(
        email='testuser@example.com',
        name='Test User',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Fixture that provides an authenticated API client.
    
    Args:
        api_client: The base API client.
        user: The user to authenticate.
    
    Returns:
        APIClient: API client authenticated as the test user.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user_data():
    """
    Fixture that provides valid user registration data.
    
    Returns:
        dict: Valid registration payload.
    """
    return {
        'email': 'newuser@example.com',
        'name': 'New User',
        'password': 'securepass123',
        'password_confirm': 'securepass123'
    }


@pytest.fixture
def login_data(user):
    """
    Fixture that provides valid login credentials.
    
    Args:
        user: The user fixture.
    
    Returns:
        dict: Valid login credentials.
    """
    return {
        'email': user.email,
        'password': 'testpass123'
    }
