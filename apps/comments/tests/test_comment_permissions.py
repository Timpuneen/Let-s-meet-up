"""
Tests for Comment API permissions.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCommentPermissions:
    """Comprehensive tests for comment permissions."""

    def test_authenticated_user_can_create_and_read(self, api_client, user, event, comment):
        """Test that authenticated users can create and read comments."""
        api_client.force_authenticate(user=user)
        
        list_url = reverse('comments:comment-list')
        detail_url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(
            list_url,
            {'event': event.id, 'content': 'New comment'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_owner_can_update_and_delete_own_comments(self, api_client, user, comment):
        """Test that comment owners can update and delete their own comments."""
        api_client.force_authenticate(user=user)
        detail_url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})

        response = api_client.patch(
            detail_url,
            {'content': 'Updated content'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_other_users_cannot_update_or_delete(self, api_client, another_user, comment):
        """Test that users cannot update or delete comments they don't own."""
        api_client.force_authenticate(user=another_user)
        detail_url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})

        response = api_client.patch(
            detail_url,
            {'content': 'Should not update'},
            format='json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_has_full_access(self, api_client, admin_user, user, event, comment):
        """Test that admin users have full CRUD access to all comments."""
        api_client.force_authenticate(user=admin_user)
        
        list_url = reverse('comments:comment-list')
        detail_url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(
            list_url,
            {'event': event.id, 'content': 'Admin comment'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = api_client.patch(
            detail_url,
            {'content': 'Admin updated'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT