"""
Tests for Category Create API endpoint (POST /api/categories/).
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.categories.models import Category


@pytest.mark.django_db
class TestCategoryCreateView:
    """Tests for creating categories."""

    def test_create_category_success(self, api_client, admin_user):
        """Test successful category creation by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-list')
        data = {
            'name': 'New Category',
            'slug': 'new-category'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Category'
        assert response.data['slug'] == 'new-category'
        assert Category.objects.filter(slug='new-category').exists()

    def test_create_category_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot create categories."""
        url = reverse('categories:category-list')
        data = {
            'name': 'New Category',
            'slug': 'new-category'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_regular_user_forbidden(self, api_client, user):
        """Test that regular users cannot create categories."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-list')
        data = {
            'name': 'New Category',
            'slug': 'new-category'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_category_missing_name(self, api_client, admin_user):
        """Test creating category without required name field."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-list')
        data = {
            'slug': 'test-slug'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_create_category_missing_slug(self, api_client, admin_user):
        """Test creating category without required slug field."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-list')
        data = {
            'name': 'Test Category'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'slug' in response.data

    def test_create_category_duplicate_slug(self, api_client, admin_user, category):
        """Test creating category with duplicate slug."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-list')
        data = {
            'name': 'Another Tech',
            'slug': 'technology'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'slug' in response.data