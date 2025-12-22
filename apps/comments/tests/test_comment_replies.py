"""
Tests for Comment Replies API endpoint (GET /api/comments/{id}/replies/).
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.comments.models import EventComment


@pytest.mark.django_db
class TestCommentRepliesView:
    """Tests for nested replies endpoint."""

    def test_get_replies_success(self, api_client, user, comment, another_user):
        """Test successful retrieval of nested replies."""
        reply1 = EventComment.objects.create(
            event=comment.event,
            user=user,
            parent=comment,
            content='First reply'
        )
        reply2 = EventComment.objects.create(
            event=comment.event,
            user=another_user,
            parent=comment,
            content='Second reply'
        )
        EventComment.objects.create(
            event=comment.event,
            user=user,
            parent=reply1,
            content='Nested reply'
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-replies', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        first_reply = next(r for r in response.data if r['content'] == 'First reply')
        assert len(first_reply['replies']) == 1
        assert first_reply['replies'][0]['content'] == 'Nested reply'

    def test_get_replies_empty(self, api_client, user, comment):
        """Test getting replies when there are none."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-replies', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_get_replies_unauthenticated(self, api_client, comment):
        """Test that unauthenticated users cannot get replies."""
        url = reverse('comments:comment-replies', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_replies_not_found(self, api_client, user):
        """Test getting replies for non-existent comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-replies', kwargs={'pk': 9999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND