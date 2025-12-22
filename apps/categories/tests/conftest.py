"""
Pytest fixtures for categories app tests.

This conftest provides fixtures specific to the categories app.
Global fixtures (api_client, user, admin_user) are inherited from root conftest.
"""
import pytest

from apps.categories.models import Category


@pytest.fixture
def category(db):
    """
    Fixture that creates a single test category.
    
    Returns:
        Category: A test category with name 'Technology'.
    """
    return Category.objects.create(
        name='Technology',
        slug='technology'
    )


@pytest.fixture
def categories(db):
    """
    Fixture that creates multiple test categories.
    
    Returns:
        list[Category]: A list of three test categories.
    """
    return [
        Category.objects.create(
            name='Technology',
            slug='technology'
        ),
        Category.objects.create(
            name='Sports',
            slug='sports'
        ),
        Category.objects.create(
            name='Music',
            slug='music'
        ),
    ]