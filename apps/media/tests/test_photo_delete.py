import pytest
from django.urls import reverse
from rest_framework import status

from apps.media.models import EventPhoto


@pytest.mark.django_db
class TestPhotoDeleteView:
    """Tests for deleting photos (DELETE /api/photos/{id}/)."""

    def test_delete_photo_success_by_uploader(self, api_client, user, photo):
        """Test successful photo deletion by uploader."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        photo.refresh_from_db()
        assert photo.is_deleted

    def test_delete_photo_success_by_organizer(self, api_client, user, another_user, event):
        """Test successful photo deletion by event organizer."""
        photo = EventPhoto.objects.create(
            event=event,
            uploaded_by=another_user,
            url='https://example.com/test.jpg'
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        photo.refresh_from_db()
        assert photo.is_deleted

    def test_delete_photo_success_by_admin(self, api_client, admin_user, photo):
        """Test successful photo deletion by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        photo.refresh_from_db()
        assert photo.is_deleted

    def test_delete_photo_forbidden_by_other_user(self, api_client, another_user, user, event):
        """Test that random users cannot delete photos."""
        photo = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/test.jpg'
        )
        
        api_client.force_authenticate(user=another_user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        photo.refresh_from_db()
        assert not photo.is_deleted

    def test_delete_photo_unauthenticated(self, api_client, photo):
        """Test that unauthenticated users cannot delete photos."""
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        photo.refresh_from_db()
        assert not photo.is_deleted

    def test_delete_photo_not_found(self, api_client, user):
        """Test deleting a non-existent photo."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': 9999})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND