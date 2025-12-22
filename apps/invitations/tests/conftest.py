import pytest
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, INVITATION_PRIVACY_EVERYONE
from apps.events.models import Event, INVITATION_PERM_PARTICIPANTS


@pytest.fixture
def organizer(db):
    """Fixture providing event organizer user."""
    return User.objects.create_user(
        email='organizer@test.com',
        name='Organizer',
        password='testpass123'
    )


@pytest.fixture
def participant(db):
    """Fixture providing participant user."""
    return User.objects.create_user(
        email='participant@test.com',
        name='Participant',
        password='testpass123'
    )


@pytest.fixture
def admin_participant(db):
    """Fixture providing admin participant user."""
    return User.objects.create_user(
        email='admin@test.com',
        name='Admin',
        password='testpass123'
    )


@pytest.fixture
def invitee(db):
    """Fixture providing user to be invited."""
    return User.objects.create_user(
        email='invitee@test.com',
        name='Invitee',
        password='testpass123',
        invitation_privacy=INVITATION_PRIVACY_EVERYONE
    )


@pytest.fixture
def event(db, organizer):
    """Fixture providing a test event."""
    return Event.objects.create(
        title='Test Event',
        description='Test Description',
        date=timezone.now() + timedelta(days=7),
        organizer=organizer,
        invitation_perm=INVITATION_PERM_PARTICIPANTS,
        max_participants=10
    )