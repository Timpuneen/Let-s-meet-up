"""
Tests for Comment List API endpoint (GET /api/comments/).
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.comments.models import EventComment


@pytest.mark.django_db
class TestCommentListView:
    """Tests for listing comments."""

    def test_list_comments_success(self, api_client, user, comments):
        """Test successful retrieval of comment list."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3

    def test_list_comments_unauthenticated(self, api_client, comments):
        """Test that unauthenticated users cannot list comments."""
        url = reverse('comments:comment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_comments_filter_by_event(self, api_client, user, event, another_event):
        """Test filtering comments by event."""
        EventComment.objects.create(event=event, user=user, content='Comment on event 1')
        EventComment.objects.create(event=event, user=user, content='Another comment on event 1')
        EventComment.objects.create(event=another_event, user=user, content='Comment on event 2')
        
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url, {'event': event.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        for comment in response.data['results']:
            assert comment['event'] == event.id

    def test_list_comments_filter_by_user(self, api_client, user, comments):
        """Test filtering comments by user."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url, {'user': user.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        for comment in response.data['results']:
            assert comment['user']['id'] == user.id

    def test_list_comments_empty(self, api_client, user):
        """Test listing when no comments exist."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_list_comments_pagination(self, api_client, user, event):
        """Test that comments are paginated."""
        for i in range(25):
            EventComment.objects.create(
                event=event,
                user=user,
                content=f'Comment {i}'
            )
        
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20