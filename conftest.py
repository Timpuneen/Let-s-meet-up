import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import User
from apps.geography.models import Country, City
from apps.categories.models import Category


# API CLIENT

@pytest.fixture
def api_client():
    """
    Fixture that provides a DRF APIClient instance for making API requests.
    
    Returns:
        APIClient: Unauthenticated API client.
    """
    return APIClient()


# USERS

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
def admin_user(db):
    """
    Fixture that creates an admin/superuser in the database.
    
    Returns:
        User: An admin user with all permissions.
    """
    return User.objects.create_superuser(
        email='admin@example.com',
        name='Admin User',
        password='adminpass123'
    )


@pytest.fixture
def another_user(db):
    """
    Fixture that creates another test user in the database.
    
    Returns:
        User: Another test user.
    """
    return User.objects.create_user(
        email='anotheruser@example.com',
        name='Another User',
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
def another_authenticated_client(api_client, another_user):
    """
    Fixture that provides another authenticated API client.
    
    Args:
        api_client: The base API client.
        another_user: The user to authenticate.
    
    Returns:
        APIClient: API client authenticated as another user.
    """
    client = APIClient()
    client.force_authenticate(user=another_user)
    return client


@pytest.fixture
def another_authenticated_client(api_client, another_user):
    """
    Fixture that provides another authenticated API client.
    
    Args:
        api_client: The base API client.
        another_user: The user to authenticate.
    
    Returns:
        APIClient: API client authenticated as another user.
    """
    client = APIClient()
    client.force_authenticate(user=another_user)
    return client


# GEOGRAPHY

@pytest.fixture
def country(db):
    """
    Fixture that creates a test country.
    
    Returns:
        Country: A test country.
    """
    return Country.objects.create(
        name='Kazakhstan',
        code='KZ'
    )


@pytest.fixture
def city(db, country):
    """
    Fixture that creates a test city.
    
    Args:
        country: Country fixture.
    
    Returns:
        City: A test city.
    """
    return City.objects.create(
        name='Almaty',
        country=country
    )


# CATEGORY

@pytest.fixture
def category(db):
    """
    Fixture that creates a test category.
    
    Returns:
        Category: A test category.
    """
    return Category.objects.create(
        name='Technology',
        slug='technology'
    )


@pytest.fixture
def another_category(db):
    """
    Fixture that creates another test category.
    
    Returns:
        Category: Another test category.
    """
    return Category.objects.create(
        name='Sports',
        slug='sports'
    )