"""
Pytest configuration and fixtures for the entire project.
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import User
from apps.events.models import Event, EVENT_STATUS_PUBLISHED
from apps.categories.models import Category
from apps.geography.models import Country, City
from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED


# ==================== USER FIXTURES ====================

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


# ==================== GEOGRAPHY FIXTURES ====================

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


# ==================== CATEGORY FIXTURES ====================

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


# ==================== EVENT FIXTURES ====================

@pytest.fixture
def event(db, user, city, category):
    """
    Fixture that creates a test event.
    
    Args:
        user: User fixture (organizer).
        city: City fixture.
        category: Category fixture.
    
    Returns:
        Event: A test event.
    """
    event = Event.objects.create(
        title='Test Event',
        description='This is a test event description',
        address='123 Test Street',
        date=timezone.now() + timedelta(days=7),
        status=EVENT_STATUS_PUBLISHED,
        max_participants=10,
        organizer=user,
        country=city.country,
        city=city
    )
    event.categories.add(category)
    return event


@pytest.fixture
def past_event(db, user, city):
    """
    Fixture that creates a past event.
    
    Args:
        user: User fixture (organizer).
        city: City fixture.
    
    Returns:
        Event: A past event.
    """
    return Event.objects.create(
        title='Past Event',
        description='This event has already happened',
        address='456 Past Lane',
        date=timezone.now() - timedelta(days=7),
        status=EVENT_STATUS_PUBLISHED,
        organizer=user,
        country=city.country,
        city=city
    )


@pytest.fixture
def full_event(db, user, city):
    """
    Fixture that creates a full event (max capacity reached).
    
    Args:
        user: User fixture (organizer).
        city: City fixture.
    
    Returns:
        Event: A full event.
    """
    event = Event.objects.create(
        title='Full Event',
        description='This event is at full capacity',
        address='789 Full Road',
        date=timezone.now() + timedelta(days=7),
        status=EVENT_STATUS_PUBLISHED,
        max_participants=1,
        organizer=user,
        country=city.country,
        city=city
    )
    # Create a participant to fill the event
    other_user = User.objects.create_user(
        email='participant@example.com',
        name='Participant',
        password='testpass123'
    )
    EventParticipant.objects.create(
        event=event,
        user=other_user,
        status=PARTICIPANT_STATUS_ACCEPTED
    )
    return event


@pytest.fixture
def event_data(city, category):
    """
    Fixture that provides valid event creation data.
    
    Args:
        city: City fixture.
        category: Category fixture.
    
    Returns:
        dict: Valid event creation payload.
    """
    return {
        'title': 'New Test Event',
        'description': 'A brand new test event',
        'address': '100 New Avenue',
        'date': (timezone.now() + timedelta(days=14)).isoformat(),
        'status': EVENT_STATUS_PUBLISHED,
        'max_participants': 20,
        'country': city.country.id,
        'city': city.id,
        'category_ids': [category.id]
    }
