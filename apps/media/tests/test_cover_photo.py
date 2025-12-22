import pytest
from django.urls import reverse
from rest_framework import status

from apps.media.models import EventPhoto


@pytest.mark.django_db
class TestCoverPhotoActions:
    """Tests for cover photo management endpoints."""

    def test_set_cover_success_by_organizer(self, api_client, user, photo):
        """Test setting photo as cover by organizer."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-set-cover', kwargs={'pk': photo.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_cover'] is True
        
        photo.refresh_from_db()
        assert photo.is_cover

    def test_set_cover_forbidden_by_non_organizer(self, api_client, another_user, photo):
        """Test that non-organizers cannot set cover photos."""
        api_client.force_authenticate(user=another_user)
        url = reverse('media:photo-set-cover', kwargs={'pk': photo.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        photo.refresh_from_db()
        assert not photo.is_cover

    def test_set_cover_success_by_admin(self, api_client, admin_user, photo):
        """Test setting photo as cover by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('media:photo-set-cover', kwargs={'pk': photo.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_cover'] is True

    def test_set_cover_replaces_existing_cover(self, api_client, user, event):
        """Test that setting new cover removes old cover."""
        photo1 = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo1.jpg',
            is_cover=True
        )
        photo2 = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo2.jpg'
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-set-cover', kwargs={'pk': photo2.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        
        photo1.refresh_from_db()
        photo2.refresh_from_db()
        assert not photo1.is_cover
        assert photo2.is_cover

    def test_remove_cover_success_by_organizer(self, api_client, user, event):
        """Test removing cover status by organizer."""
        photo = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo.jpg',
            is_cover=True
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-remove-cover', kwargs={'pk': photo.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_cover'] is False
        
        photo.refresh_from_db()
        assert not photo.is_cover

    def test_remove_cover_forbidden_by_non_organizer(self, api_client, another_user, event, user):
        """Test that non-organizers cannot remove cover status."""
        photo = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo.jpg',
            is_cover=True
        )
        
        api_client.force_authenticate(user=another_user)
        url = reverse('media:photo-remove-cover', kwargs={'pk': photo.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        photo.refresh_from_db()
        assert photo.is_cover