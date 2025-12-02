"""
Tests for Photo API endpoints.

This module contains comprehensive tests for PhotoViewSet
including CRUD operations, permissions, filtering, and cover photo management.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from apps.events.models import Event
from apps.geography.models import Country, City
from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED
from .models import EventPhoto


# ============== FIXTURES ==============

@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Fixture for regular authenticated user."""
    return User.objects.create_user(
        email='user@example.com',
        password='testpass123',
        name='Test User'
    )


@pytest.fixture
def another_user(db):
    """Fixture for another regular user."""
    return User.objects.create_user(
        email='another@example.com',
        password='testpass123',
        name='Another User'
    )


@pytest.fixture
def admin_user(db):
    """Fixture for admin user."""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        name='Admin User'
    )


@pytest.fixture
def country(db):
    """Fixture for a test country."""
    return Country.objects.create(
        name='Test Country',
        code='TC'
    )


@pytest.fixture
def city(db, country):
    """Fixture for a test city."""
    return City.objects.create(
        name='Test City',
        country=country
    )


@pytest.fixture
def event(db, user, country, city):
    """Fixture for a test event."""
    from datetime import datetime, timedelta
    return Event.objects.create(
        title='Test Event',
        description='Test event description',
        address='123 Test Street',
        date=datetime.now() + timedelta(days=7),
        organizer=user,
        country=country,
        city=city
    )


@pytest.fixture
def photo(db, event, user):
    """Fixture for a test photo."""
    return EventPhoto.objects.create(
        event=event,
        uploaded_by=user,
        url='https://example.com/photo.jpg',
        caption='Test photo'
    )


@pytest.fixture
def photos(db, event, user, another_user):
    """Fixture for multiple test photos."""
    return [
        EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo1.jpg',
            caption='First photo'
        ),
        EventPhoto.objects.create(
            event=event,
            uploaded_by=another_user,
            url='https://example.com/photo2.jpg',
            caption='Second photo'
        ),
        EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo3.jpg',
            caption='Third photo',
            is_cover=True
        ),
    ]


# ============== LIST TESTS ==============

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
        # Cover photo should be first
        assert response.data['results'][0]['is_cover'] is True

    def test_list_photos_unauthenticated(self, api_client, photos):
        """Test that unauthenticated users cannot list photos."""
        url = reverse('media:photo-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_photos_filter_by_event(self, api_client, user, event, another_user, country, city):
        """Test filtering photos by event."""
        from datetime import datetime, timedelta
        
        # Create another event
        another_event = Event.objects.create(
            title='Another Event',
            description='Another event description',
            address='456 Test Street',
            date=datetime.now() + timedelta(days=14),
            organizer=another_user,
            country=country,
            city=city
        )
        
        # Create photos for both events
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
        # Create more photos than page size
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
        assert len(response.data['results']) == 20  # Default page size


# ============== RETRIEVE TESTS ==============

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


# ============== CREATE TESTS ==============

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
        # Make user a participant
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


# ============== UPDATE TESTS ==============

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


# ============== DELETE TESTS ==============

@pytest.mark.django_db
class TestPhotoDeleteView:
    """Tests for deleting photos (DELETE /api/photos/{id}/)."""

    def test_delete_photo_success_by_uploader(self, api_client, user, photo):
        """Test successful photo deletion by uploader."""
        api_client.force_authenticate(user=user)
        url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Soft delete - object still exists but is_deleted is True
        photo.refresh_from_db()
        assert photo.is_deleted

    def test_delete_photo_success_by_organizer(self, api_client, user, another_user, event):
        """Test successful photo deletion by event organizer."""
        # Another user uploads photo
        photo = EventPhoto.objects.create(
            event=event,
            uploaded_by=another_user,
            url='https://example.com/test.jpg'
        )
        
        # Organizer (user) deletes it
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


# ============== COVER PHOTO TESTS ==============

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
        # Create two photos
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
        
        # Set photo2 as cover
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


# ============== EVENT PHOTOS ENDPOINT TESTS ==============

@pytest.mark.django_db
class TestEventPhotosView:
    """Tests for event photos endpoint (GET /api/events/{id}/photos/)."""

    def test_get_event_photos_success(self, api_client, user, event):
        """Test retrieving photos for an event."""
        # Create photos for the event
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
        
        # Cover photo should be first
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
        from datetime import datetime, timedelta
        
        # Create another event
        another_event = Event.objects.create(
            title='Another Event',
            description='Another description',
            date=datetime.now() + timedelta(days=14),
            organizer=user,
            city=city
        )
        
        # Create photos for both events
        EventPhoto.objects.create(event=event, uploaded_by=user, url='https://example.com/1.jpg')
        EventPhoto.objects.create(event=another_event, uploaded_by=user, url='https://example.com/2.jpg')
        
        api_client.force_authenticate(user=user)
        url = reverse('events:event-photos', kwargs={'pk': event.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['url'] == 'https://example.com/1.jpg'


# ============== PERMISSION TESTS ==============

@pytest.mark.django_db
class TestPhotoPermissions:
    """Comprehensive tests for photo permissions."""

    def test_organizer_can_upload_and_manage(self, api_client, user, event):
        """Test that event organizers have full photo management access."""
        api_client.force_authenticate(user=user)
        
        list_url = reverse('media:photo-list')

        # Can upload
        response = api_client.post(
            list_url,
            {'event': event.id, 'url': 'https://example.com/photo.jpg'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        photo_id = response.data['id']
        
        detail_url = reverse('media:photo-detail', kwargs={'pk': photo_id})
        
        # Can update
        response = api_client.patch(
            detail_url,
            {'caption': 'Updated'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Can delete
        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_participant_can_upload_but_limited_delete(self, api_client, another_user, user, event):
        """Test that participants can upload but have limited permissions."""
        # Make another_user a participant
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=another_user)
        list_url = reverse('media:photo-list')
        
        # Can upload
        response = api_client.post(
            list_url,
            {'event': event.id, 'url': 'https://example.com/photo.jpg'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        photo_id = response.data['id']
        
        # Can update own photo
        detail_url = reverse('media:photo-detail', kwargs={'pk': photo_id})
        response = api_client.patch(
            detail_url,
            {'caption': 'Updated'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Can delete own photo
        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_admin_has_full_access(self, api_client, admin_user, user, event):
        """Test that admin users have full access to all photos."""
        # Create photo as regular user
        photo = EventPhoto.objects.create(
            event=event,
            uploaded_by=user,
            url='https://example.com/photo.jpg'
        )
        
        api_client.force_authenticate(user=admin_user)
        detail_url = reverse('media:photo-detail', kwargs={'pk': photo.pk})
        
        # Can delete others' photos
        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

