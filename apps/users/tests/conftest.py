import pytest

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