import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPhotoUpdateView:
    """Tests for updating photos (PUT/PATCH /api/photos/{id}/)."""

    def test_update_photo_success_by_uploader(self, api_client, user, photo):
        """Test successful photo update by uploader."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        data = {
            'caption': 'Updated caption'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['caption'] == 'Updated caption'
        
        photo.refresh_from_db()
        assert photo.caption == 'Updated caption'

    def test_update_photo_url(self, api_client, user, photo):
        """Test updating photo URL."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        data = {
            'url': 'https://example.com/updated-photo.jpg'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['url'] == 'https://example.com/updated-photo.jpg'

    def test_update_photo_forbidden_by_other_user(self, api_client, another_user, photo):
        """Test that other users cannot update photos they didn't upload."""
        api_client.force_authenticate(user=another_user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        data = {
            'caption': 'Should not update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        photo.refresh_from_db()
        assert photo.caption == 'Test photo'

    def test_update_photo_unauthenticated(self, api_client, photo):
        """Test that unauthenticated users cannot update photos."""
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        data = {
            'caption': 'Should not update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_photo_not_found(self, api_client, user):
        """Test updating a non-existent photo."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': 9999})
        data = {
            'caption': 'Does not exist'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND