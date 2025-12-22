import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPhotoRetrieveView:
    """Tests for retrieving photo details (GET /api/photos/{id}/)."""

    def test_retrieve_photo_success(self, api_client, user, photo):
        """Test successful retrieval of photo details."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == photo.id
        assert response.data['url'] == 'https://example.com/photo.jpg'
        assert response.data['caption'] == 'Test photo'
        assert 'uploaded_by' in response.data

    def test_retrieve_photo_not_found(self, api_client, user):
        """Test retrieving a non-existent photo."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': 9999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_photo_unauthenticated(self, api_client, photo):
        """Test that unauthenticated users cannot retrieve photos."""
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED