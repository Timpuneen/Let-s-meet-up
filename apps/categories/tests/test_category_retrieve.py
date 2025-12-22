"""
Tests for Category Retrieve API endpoint (GET /api/categories/{id}/).
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCategoryRetrieveView:
    """Tests for retrieving category details."""

    def test_retrieve_category_success(self, api_client, category):
        """Test successful retrieval of category details."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id
        assert response.data['name'] == 'Technology'
        assert response.data['slug'] == 'technology'

    def test_retrieve_category_not_found(self, api_client):
        """Test retrieving a non-existent category."""
        url = reverse('categories:category-detail', kwargs={'pk': 9999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_category_authenticated(self, api_client, user, category):
        """Test that authenticated users can retrieve category details."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == category.id