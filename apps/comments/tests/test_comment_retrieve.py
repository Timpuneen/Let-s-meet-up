"""
Tests for Comment Retrieve API endpoint (GET /api/comments/{id}/).
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCommentRetrieveView:
    """Tests for retrieving comment details."""

    def test_retrieve_comment_success(self, api_client, user, comment):
        """Test successful retrieval of comment details."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == comment.id
        assert response.data['content'] == 'This is a test comment'
        assert 'user' in response.data
        assert 'depth' in response.data
        assert 'reply_count' in response.data

    def test_retrieve_comment_not_found(self, api_client, user):
        """Test retrieving a non-existent comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': 9999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_comment_unauthenticated(self, api_client, comment):
        """Test that unauthenticated users cannot retrieve comments."""
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED