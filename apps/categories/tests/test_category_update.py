"""
Tests for Category Update API endpoint (PUT/PATCH /api/categories/{id}/).
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCategoryUpdateView:
    """Tests for updating categories."""

    def test_update_category_success(self, api_client, admin_user, category):
        """Test successful category update by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {
            'name': 'Updated Technology',
            'slug': 'updated-technology'
        }
        response = api_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Technology'
        assert response.data['slug'] == 'updated-technology'
        
        category.refresh_from_db()
        assert category.name == 'Updated Technology'
        assert category.slug == 'updated-technology'

    def test_partial_update_category_success(self, api_client, admin_user, category):
        """Test successful partial category update by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {
            'name': 'Partially Updated'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Partially Updated'
        assert response.data['slug'] == 'technology'
        
        category.refresh_from_db()
        assert category.name == 'Partially Updated'
        assert category.slug == 'technology'

    def test_update_category_unauthenticated(self, api_client, category):
        """Test that unauthenticated users cannot update categories."""
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {
            'name': 'Should Not Update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_category_regular_user_forbidden(self, api_client, user, category):
        """Test that regular users cannot update categories."""
        api_client.force_authenticate(user=user)
        url = reverse('categories:category-detail', kwargs={'pk': category.pk})
        data = {
            'name': 'Should Not Update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_category_not_found(self, api_client, admin_user):
        """Test updating a non-existent category."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': 9999})
        data = {
            'name': 'Does Not Exist'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category_duplicate_slug(self, api_client, admin_user, categories):
        """Test updating category with duplicate slug."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('categories:category-detail', kwargs={'pk': categories[0].pk})
        data = {
            'slug': 'sports'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST