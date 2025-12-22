import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.events.models import Event, EVENT_STATUS_PUBLISHED


@pytest.mark.django_db
class TestEventCommentsView:
    """Test suite for event comments endpoint."""
    
    def test_get_event_comments_success(self, authenticated_client, event, user, another_user):
        """Test retrieving comments for an event (Good case)."""
        from apps.comments.models import EventComment
        
        comment1 = EventComment.objects.create(
            event=event,
            user=user,
            content='First comment'
        )
        comment2 = EventComment.objects.create(
            event=event,
            user=another_user,
            content='Second comment'
        )
        
        url = reverse('events:event-comments', kwargs={'pk': event.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['event'] == event.id
        assert response.data['event_title'] == event.title
        assert len(response.data['results']) == 2
        
        assert response.data['results'][0]['content'] == 'First comment'
        assert response.data['results'][1]['content'] == 'Second comment'
    
    def test_get_event_comments_empty(self, authenticated_client, event):
        """Test getting comments when event has none (Bad case 1)."""
        url = reverse('events:event-comments', kwargs={'pk': event.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
    
    def test_get_event_comments_unauthenticated(self, api_client, event):
        """Test accessing event comments without authentication (Bad case 2)."""
        url = reverse('events:event-comments', kwargs={'pk': event.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_event_comments_not_found(self, authenticated_client):
        """Test getting comments for non-existent event (Bad case 3)."""
        url = reverse('events:event-comments', kwargs={'pk': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_event_comments_with_replies(self, authenticated_client, event, user, another_user):
        """Test that nested replies are included in results."""
        from apps.comments.models import EventComment
        
        parent = EventComment.objects.create(
            event=event,
            user=user,
            content='Parent comment'
        )
        
        reply = EventComment.objects.create(
            event=event,
            user=another_user,
            parent=parent,
            content='Reply to parent'
        )
        
        url = reverse('events:event-comments', kwargs={'pk': event.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        contents = [c['content'] for c in response.data['results']]
        assert 'Parent comment' in contents
        assert 'Reply to parent' in contents
    
    def test_get_event_comments_only_for_specific_event(self, authenticated_client, event, user, city):
        """Test that only comments for the specific event are returned."""
        from apps.comments.models import EventComment
        
        another_event = Event.objects.create(
            title='Another Event',
            description='Another description',
            date=timezone.now() + timedelta(days=14),
            organizer=user,
            city=city,
            status=EVENT_STATUS_PUBLISHED
        )
        
        EventComment.objects.create(event=event, user=user, content='Comment for event 1')
        EventComment.objects.create(event=another_event, user=user, content='Comment for event 2')
        
        url = reverse('events:event-comments', kwargs={'pk': event.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['content'] == 'Comment for event 1'