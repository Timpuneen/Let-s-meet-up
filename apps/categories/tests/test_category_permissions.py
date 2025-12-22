"""
Tests for Category API permissions.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCategoryPermissions:
    """Comprehensive tests for category permissions."""

    def test_anonymous_can_read_only(self, api_client, category):
        """Test that anonymous users have read-only access."""
        list_url = reverse('categories:category-list')
        detail_url = reverse('categories:category-detail', kwargs={'pk': category.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(list_url, {'name': 'Test', 'slug': 'test'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = api_client.patch(detail_url, {'name': 'Test'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_can_read_only(self, api_client, user, category):
        """Test that regular authenticated users have read-only access."""
        api_client.force_authenticate(user=user)
        
        list_url = reverse('categories:category-list')
        detail_url = reverse('categories:category-detail', kwargs={'pk': category.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(list_url, {'name': 'Test', 'slug': 'test'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = api_client.patch(detail_url, {'name': 'Test'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_has_full_access(self, api_client, admin_user, category):
        """Test that admin users have full CRUD access."""
        api_client.force_authenticate(user=admin_user)
        
        list_url = reverse('categories:category-list')
        detail_url = reverse('categories:category-detail', kwargs={'pk': category.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(
            list_url,
            {'name': 'Admin Category', 'slug': 'admin-category'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = api_client.patch(
            detail_url,
            {'name': 'Updated by Admin'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT