import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework import status

from apps.events.models import Event
from apps.media.models import EventPhoto


@pytest.mark.django_db
class TestEventPhotosView:
    """Tests for event photos endpoint (GET /api/events/{id}/photos/)."""

    def test_get_event_photos_success(self, api_client, user, event):
        """Test retrieving photos for an event."""
        photo1 = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo1.jpg',
            caption='First photo'
        )
        photo2 = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo2.jpg',
            caption='Second photo',
            is_cover=True
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('events:event-photos', kwargs={'pk': event.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['event'] == event.id
        assert response.data['event_title'] == event.title
        assert len(response.data['results']) == 2
        
        assert response.data['results'][0]['is_cover'] is True
        assert response.data['results'][0]['caption'] == 'Second photo'

    def test_get_event_photos_empty(self, api_client, user, event):
        """Test getting photos when event has none."""
        api_client.force_authenticate(user=user)
        url = reverse('events:event-photos', kwargs={'pk': event.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0

    def test_get_event_photos_unauthenticated(self, api_client, event):
        """Test accessing event photos without authentication."""
        url = reverse('events:event-photos', kwargs={'pk': event.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_event_photos_not_found(self, api_client, user):
        """Test getting photos for non-existent event."""
        api_client.force_authenticate(user=user)
        url = reverse('events:event-photos', kwargs={'pk': 99999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_event_photos_only_for_specific_event(self, api_client, user, event, city):
        """Test that only photos for the specific event are returned."""
        another_event = Event.objects.create(
            title='Another Event',
            description='Another description',
            date=datetime.now() + timedelta(days=14),
            organizer=user,
            city=city
        )
        
        EventPhoto.objects.create(event=event, uploaded_by=user, url='https://example.com/1.jpg')
        EventPhoto.objects.create(event=another_event, uploaded_by=user, url='https://example.com/2.jpg')
        
        api_client.force_authenticate(user=user)
        url = reverse('events:event-photos', kwargs={'pk': event.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['url'] == 'https://example.com/1.jpg'