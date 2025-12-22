import pytest
from datetime import timedelta
from django.utils import timezone

from apps.events.models import Event, EVENT_STATUS_PUBLISHED
from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED
from apps.users.models import User

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