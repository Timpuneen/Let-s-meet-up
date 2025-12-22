import pytest
from datetime import datetime, timedelta

from apps.events.models import Event
from apps.media.models import EventPhoto


@pytest.fixture
def event(db, user, country, city):
    """Fixture for a test event."""
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
def photo(db, event, user):
    """Fixture for a single test photo."""
    return EventPhoto.objects.create(
        event=event,
        uploaded_by=user,
        url='https://example.com/photo.jpg',
        caption='Test photo'
    )


@pytest.fixture
def photos(db, event, user, another_user):
    """Fixture for multiple test photos."""
    return [
        EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo1.jpg',
            caption='First photo'
        ),
        EventPhoto.objects.create(
            event=event,
            uploaded_by=another_user,
            url='https://example.com/photo2.jpg',
            caption='Second photo'
        ),
        EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo3.jpg',
            caption='Third photo',
            is_cover=True
        ),
    ]