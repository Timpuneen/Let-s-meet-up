"""
Tests for Comment Delete API endpoint (DELETE /api/comments/{id}/).
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCommentDeleteView:
    """Tests for deleting comments."""

    def test_delete_comment_success_by_owner(self, api_client, user, comment):
        """Test successful comment deletion by owner."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        comment.refresh_from_db()
        assert comment.is_deleted

    def test_delete_comment_success_by_admin(self, api_client, admin_user, comment):
        """Test successful comment deletion by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        comment.refresh_from_db()
        assert comment.is_deleted

    def test_delete_comment_forbidden_by_other_user(self, api_client, another_user, comment):
        """Test that other users cannot delete comments they don't own."""
        api_client.force_authenticate(user=another_user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        comment.refresh_from_db()
        assert not comment.is_deleted

    def test_delete_comment_unauthenticated(self, api_client, comment):
        """Test that unauthenticated users cannot delete comments."""
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        comment.refresh_from_db()
        assert not comment.is_deleted

    def test_delete_comment_not_found(self, api_client, user):
        """Test deleting a non-existent comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': 9999})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND