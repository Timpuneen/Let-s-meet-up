"""
Tests for Category Delete API endpoint (DELETE /api/categories/{id}/).
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.categories.models import Category


@pytest.mark.django_db
class TestCategoryDeleteView:
    """Tests for deleting categories."""

    def test_delete_category_success(self, api_client, admin_user, category):
        """Test successful category deletion by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(pk=category.pk).exists()

    def test_delete_category_unauthenticated(self, api_client, category):
        """Test that unauthenticated users cannot delete categories."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Category.objects.filter(pk=category.pk).exists()

    def test_delete_category_regular_user_forbidden(self, api_client, user, category):
        """Test that regular users cannot delete categories."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Category.objects.filter(pk=category.pk).exists()

    def test_delete_category_not_found(self, api_client, admin_user):
        """Test deleting a non-existent category."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': 9999})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND