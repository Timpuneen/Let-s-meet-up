"""
Tests for Comment Update API endpoint (PUT/PATCH /api/comments/{id}/).
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCommentUpdateView:
    """Tests for updating comments."""

    def test_update_comment_success_by_owner(self, api_client, user, comment):
        """Test successful comment update by owner."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        data = {
            'content': 'Updated comment content'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Updated comment content'
        
        comment.refresh_from_db()
        assert comment.content == 'Updated comment content'

    def test_update_comment_success_by_admin(self, api_client, admin_user, comment):
        """Test successful comment update by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        data = {
            'content': 'Admin updated content'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Admin updated content'

    def test_update_comment_forbidden_by_other_user(self, api_client, another_user, comment):
        """Test that other users cannot update comments they don't own."""
        api_client.force_authenticate(user=another_user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        data = {
            'content': 'Should not update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        comment.refresh_from_db()
        assert comment.content == 'This is a test comment'

    def test_update_comment_unauthenticated(self, api_client, comment):
        """Test that unauthenticated users cannot update comments."""
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        data = {
            'content': 'Should not update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_comment_not_found(self, api_client, user):
        """Test updating a non-existent comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': 9999})
        data = {
            'content': 'Does not exist'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND