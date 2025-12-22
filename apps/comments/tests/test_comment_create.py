"""
Tests for Comment Create API endpoint (POST /api/comments/).
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.comments.models import EventComment


@pytest.mark.django_db
class TestCommentCreateView:
    """Tests for creating comments."""

    def test_create_comment_success(self, api_client, user, event):
        """Test successful comment creation by authenticated user."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'event': event.id,
            'content': 'This is a new comment'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'This is a new comment'
        assert response.data['user']['id'] == user.id
        assert response.data['event'] == event.id
        assert EventComment.objects.filter(content='This is a new comment').exists()

    def test_create_comment_reply_success(self, api_client, user, comment):
        """Test successful creation of a reply to a comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'event': comment.event.id,
            'parent': comment.id,
            'content': 'This is a reply'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['parent'] == comment.id
        assert response.data['content'] == 'This is a reply'
        assert response.data['depth'] == 1

    def test_create_comment_unauthenticated(self, api_client, event):
        """Test that unauthenticated users cannot create comments."""
        url = reverse('comments:comment-list')
        data = {
            'event': event.id,
            'content': 'Should not be created'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_comment_missing_content(self, api_client, user, event):
        """Test creating comment without required content field."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'event': event.id
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data

    def test_create_comment_missing_event(self, api_client, user):
        """Test creating comment without required event field."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'content': 'Test comment'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'event' in response.data

    def test_create_comment_invalid_parent_event(self, api_client, user, event, another_event, another_user):
        """Test creating reply with parent from different event."""
        another_comment = EventComment.objects.create(
            event=another_event,
            user=another_user,
            content='Comment on another event'
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'event': event.id,
            'parent': another_comment.id,
            'content': 'This should fail'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'parent' in response.data