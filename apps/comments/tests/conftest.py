"""
Pytest fixtures for comments app tests.

This conftest provides fixtures specific to the comments app.
Global fixtures (api_client, user, admin_user, another_user, country, city) 
are inherited from root conftest.
"""
import pytest
from datetime import datetime, timedelta

from apps.events.models import Event
from apps.comments.models import EventComment


@pytest.fixture
def event(db, user, country, city):
    """
    Fixture that creates a test event.
    
    Args:
        user: Event organizer.
        country: Event country.
        city: Event city.
    
    Returns:
        Event: A test event scheduled for 7 days from now.
    """
    return Event.objects.create(
        title='Test Event',
        description='Test event description',
        address='123 Test Street',
        date=datetime.now() + timedelta(days=7),
        organizer=user,
        country=country,
        city=city
    )


@pytest.fixture
def another_event(db, another_user, country, city):
    """
    Fixture that creates another test event.
    
    Args:
        another_user: Event organizer.
        country: Event country.
        city: Event city.
    
    Returns:
        Event: Another test event scheduled for 14 days from now.
    """
    return Event.objects.create(
        title='Another Event',
        description='Another event description',
        address='456 Test Street',
        date=datetime.now() + timedelta(days=14),
        organizer=another_user,
        country=country,
        city=city
    )


@pytest.fixture
def comment(db, event, user):
    """
    Fixture that creates a single test comment.
    
    Args:
        event: Event the comment belongs to.
        user: Comment author.
    
    Returns:
        EventComment: A test comment.
    """
    return EventComment.objects.create(
        event=event,
        user=user,
        content='This is a test comment'
    )


@pytest.fixture
def comments(db, event, user, another_user):
    """
    Fixture that creates multiple test comments.
    
    Args:
        event: Event the comments belong to.
        user: First comment author.
        another_user: Second comment author.
    
    Returns:
        list[EventComment]: A list of three test comments.
    """
    return [
        EventComment.objects.create(
            event=event,
            user=user,
            content='First comment'
        ),
        EventComment.objects.create(
            event=event,
            user=another_user,
            content='Second comment'
        ),
        EventComment.objects.create(
            event=event,
            user=user,
            content='Third comment'
        ),
    ]