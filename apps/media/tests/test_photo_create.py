import pytest
from django.urls import reverse
from rest_framework import status

from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED
from apps.media.models import EventPhoto


@pytest.mark.django_db
class TestPhotoCreateView:
    """Tests for creating photos (POST /api/photos/)."""

    def test_create_photo_success_as_organizer(self, api_client, user, event):
        """Test successful photo creation by event organizer."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-list')
        data = {
            'event': event.id,
            'url': 'https://example.com/new-photo.jpg',
            'caption': 'New photo'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['url'] == 'https://example.com/new-photo.jpg'
        assert response.data['caption'] == 'New photo'
        assert response.data['uploaded_by']['id'] == user.id
        assert EventPhoto.objects.filter(url='https://example.com/new-photo.jpg').exists()

    def test_create_photo_success_as_participant(self, api_client, another_user, event):
        """Test successful photo creation by event participant."""
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=another_user)
        url = reverse('media:photo-list')
        data = {
            'event': event.id,
            'url': 'https://example.com/participant-photo.jpg',
            'caption': 'Participant photo'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['uploaded_by']['id'] == another_user.id

    def test_create_photo_forbidden_not_participant(self, api_client, another_user, event):
        """Test that non-participants cannot upload photos."""
        api_client.force_authenticate(user=another_user)
        url = reverse('media:photo-list')
        data = {
            'event': event.id,
            'url': 'https://example.com/photo.jpg',
            'caption': 'Should not work'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'event' in response.data

    def test_create_photo_unauthenticated(self, api_client, event):
        """Test that unauthenticated users cannot create photos."""
        url = reverse('media:photo-list')
        data = {
            'event': event.id,
            'url': 'https://example.com/photo.jpg'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_photo_invalid_url(self, api_client, user, event):
        """Test creating photo with invalid URL format."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-list')
        data = {
            'event': event.id,
            'url': 'not-a-valid-url'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'url' in response.data

    def test_create_photo_missing_url(self, api_client, user, event):
        """Test creating photo without URL."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-list')
        data = {
            'event': event.id,
            'caption': 'No URL'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'url' in response.data