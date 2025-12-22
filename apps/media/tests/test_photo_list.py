import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework import status

from apps.events.models import Event
from apps.media.models import EventPhoto


@pytest.mark.django_db
class TestPhotoListView:
    """Tests for listing photos (GET /api/photos/)."""

    def test_list_photos_success(self, api_client, user, photos):
        """Test successful retrieval of photo list."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3
        assert response.data['results'][0]['is_cover'] is True

    def test_list_photos_unauthenticated(self, api_client, photos):
        """Test that unauthenticated users cannot list photos."""
        url = reverse('media:photo-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_photos_filter_by_event(self, api_client, user, event, another_user, country, city):
        """Test filtering photos by event."""
        another_event = Event.objects.create(
            title='Another Event',
            description='Another event description',
            address='456 Test Street',
            date=datetime.now() + timedelta(days=14),
            organizer=another_user,
            country=country,
            city=city
        )
        
        EventPhoto.objects.create(event=event, uploaded_by=user, url='https://example.com/1.jpg')
        EventPhoto.objects.create(event=event, uploaded_by=user, url='https://example.com/2.jpg')
        EventPhoto.objects.create(event=another_event, uploaded_by=user, url='https://example.com/3.jpg')
        
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-list')
        response = api_client.get(url, {'event': event.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        for photo in response.data['results']:
            assert photo['event'] == event.id

    def test_list_photos_filter_by_user(self, api_client, user, photos):
        """Test filtering photos by uploader."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-list')
        response = api_client.get(url, {'user': user.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        for photo in response.data['results']:
            assert photo['uploaded_by']['id'] == user.id

    def test_list_photos_empty(self, api_client, user):
        """Test listing when no photos exist."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_list_photos_pagination(self, api_client, user, event):
        """Test that photos are paginated."""
        for i in range(25):
            EventPhoto.objects.create(
                event=event,
                uploaded_by=user,
                url=f'https://example.com/photo{i}.jpg'
            )
        
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20