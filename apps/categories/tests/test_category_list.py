"""
Tests for Category List API endpoint (GET /api/categories/).
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCategoryListView:
    """Tests for listing categories."""

    def test_list_categories_success(self, api_client, categories):
        """Test successful retrieval of category list."""
        url = reverse('categories:category-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]['name'] == 'Music'
        assert 'slug' in response.data[0]

    def test_list_categories_empty(self, api_client):
        """Test listing when no categories exist."""
        url = reverse('categories:category-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_categories_authenticated(self, api_client, user, categories):
        """Test that authenticated users can also list categories."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3