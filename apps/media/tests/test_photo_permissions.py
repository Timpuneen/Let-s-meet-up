import pytest
from django.urls import reverse
from rest_framework import status

from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED
from apps.media.models import EventPhoto


@pytest.mark.django_db
class TestPhotoPermissions:
    """Comprehensive tests for photo permissions."""

    def test_organizer_can_upload_and_manage(self, api_client, user, event):
        """Test that event organizers have full photo management access."""
        api_client.force_authenticate(user=user)
        
        list_url = reverse('media:photo-list')

        response = api_client.post(
            list_url,
            {'event': event.id, 'url': 'https://example.com/photo.jpg'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        photo_id = response.data['id']
        
        detail_url = reverse('media:photo-detail', kwargs={'pk': photo_id})
        
        response = api_client.patch(
            detail_url,
            {'caption': 'Updated'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_participant_can_upload_but_limited_delete(self, api_client, another_user, user, event):
        """Test that participants can upload but have limited permissions."""
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=another_user)
        list_url = reverse('media:photo-list')
        
        response = api_client.post(
            list_url,
            {'event': event.id, 'url': 'https://example.com/photo.jpg'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        photo_id = response.data['id']
        
        detail_url = reverse('media:photo-detail', kwargs={'pk': photo_id})
        
        response = api_client.patch(
            detail_url,
            {'caption': 'Updated'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_admin_has_full_access(self, api_client, admin_user, user, event):
        """Test that admin users have full access to all photos."""
        photo = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo.jpg'
        )
        
        api_client.force_authenticate(user=admin_user)
        detail_url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        
        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT