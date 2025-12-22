import pytest

from apps.users.models import User


@pytest.fixture
def user1(db):
    """Fixture providing first test user."""
    return User.objects.create_user(
        email='user1@test.com',
        name='User One',
        password='testpass123'
    )


@pytest.fixture
def user2(db):
    """Fixture providing second test user."""
    return User.objects.create_user(
        email='user2@test.com',
        name='User Two',
        password='testpass123'
    )


@pytest.fixture
def user3(db):
    """Fixture providing third test user."""
    return User.objects.create_user(
        email='user3@test.com',
        name='User Three',
        password='testpass123'
    )