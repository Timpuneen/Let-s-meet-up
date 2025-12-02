"""
Unit tests for event endpoints using pytest.

Tests cover event CRUD operations, registration/unregistration,
and custom endpoints like my_organized and my_registered.
Each endpoint is tested with one success case and three failure cases.
"""

import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.events.models import Event, EVENT_STATUS_PUBLISHED
from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED


# ==================== LIST EVENTS TESTS ====================

@pytest.mark.django_db
class TestEventListView:
    """Test suite for event listing endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('events:event-list')
    
    def test_list_events_success(self, api_client, event, past_event):
        """Test listing events returns only upcoming events (Good case)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        # Should only include upcoming event, not past event
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == event.title
    
    def test_list_events_empty(self, api_client):
        """Test listing when no events exist (Bad case 1)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
    
    def test_list_events_pagination(self, api_client, user, city):
        """Test pagination works correctly (Bad case 2)."""
        # Create multiple events
        for i in range(15):
            Event.objects.create(
                title=f'Event {i}',
                description=f'Description {i}',
                date=timezone.now() + timedelta(days=i+1),
                organizer=user,
                city=city,
                country=city.country
            )
        
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
    


# ==================== RETRIEVE EVENT TESTS ====================

@pytest.mark.django_db
class TestEventRetrieveView:
    """Test suite for event detail endpoint."""
    
    def test_retrieve_event_success(self, api_client, event):
        """Test retrieving event details (Good case)."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == event.title
        assert response.data['description'] == event.description
        assert 'organizer' in response.data
        assert 'participants_count' in response.data
        assert 'category_names' in response.data
    
    def test_retrieve_nonexistent_event(self, api_client):
        """Test retrieving non-existent event (Bad case 1)."""
        url = reverse('events:event-detail', kwargs={'pk': 99999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_retrieve_deleted_event(self, api_client, event):
        """Test retrieving soft-deleted event (Bad case 2)."""
        event.delete()  # Soft delete
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_retrieve_event_includes_categories(self, api_client, event, another_category):
        """Test that retrieved event includes all categories (Bad case 3)."""
        event.categories.add(another_category)
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['category_names']) == 2


# ==================== CREATE EVENT TESTS ====================

@pytest.mark.django_db
class TestEventCreateView:
    """Test suite for event creation endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('events:event-list')
    
    def test_create_event_success(self, authenticated_client, event_data):
        """Test successful event creation (Good case)."""
        response = authenticated_client.post(self.url, event_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == event_data['title']
        assert response.data['description'] == event_data['description']
        # EventCreateSerializer doesn't return organizer in response
        # Verify event was created in database with correct organizer
        created_event = Event.objects.get(title=event_data['title'])
        assert created_event.organizer == authenticated_client.handler._force_user
    
    def test_create_event_unauthenticated(self, api_client, event_data):
        """Test creating event without authentication (Bad case 1)."""
        response = api_client.post(self.url, event_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_event_past_date(self, authenticated_client, event_data):
        """Test creating event with past date (Bad case 2)."""
        event_data['date'] = (timezone.now() - timedelta(days=1)).isoformat()
        response = authenticated_client.post(self.url, event_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'date' in response.data
    
    def test_create_event_invalid_city_country(self, authenticated_client, event_data, country):
        """Test creating event with city that doesn't belong to country (Bad case 3)."""
        # Create another country
        other_country = country.__class__.objects.create(name='Russia', code='RU')
        event_data['country'] = other_country.id
        # city still belongs to original country
        
        response = authenticated_client.post(self.url, event_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ==================== UPDATE EVENT TESTS ====================

@pytest.mark.django_db
class TestEventUpdateView:
    """Test suite for event update endpoint."""
    
    def test_update_event_success(self, authenticated_client, event):
        """Test successful event update by organizer (Good case)."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        update_data = {
            'title': 'Updated Title',
            'description': event.description,
            'date': event.date.isoformat(),
            'address': event.address,
            'status': event.status,
        }
        response = authenticated_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'
        
        # Verify update in database
        event.refresh_from_db()
        assert event.title == 'Updated Title'
    
    def test_update_event_not_organizer(self, another_authenticated_client, event):
        """Test updating event by non-organizer (Bad case 1)."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        update_data = {'title': 'Hacked Title'}
        response = another_authenticated_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_event_unauthenticated(self, api_client, event):
        """Test updating event without authentication (Bad case 2)."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        update_data = {'title': 'Unauthenticated Update'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_event_max_participants_below_current(self, authenticated_client, event, another_user):
        """Test reducing max_participants below current count (Bad case 3)."""
        # Add a participant
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        update_data = {'max_participants': 0}  # Current count is 1
        response = authenticated_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ==================== DELETE EVENT TESTS ====================

@pytest.mark.django_db
class TestEventDeleteView:
    """Test suite for event deletion endpoint."""
    
    def test_delete_event_success(self, authenticated_client, event):
        """Test successful event deletion by organizer (Good case)."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify soft delete
        event.refresh_from_db()
        assert event.is_deleted is True
    
    def test_delete_event_not_organizer(self, another_authenticated_client, event):
        """Test deleting event by non-organizer (Bad case 1)."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = another_authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_event_unauthenticated(self, api_client, event):
        """Test deleting event without authentication (Bad case 2)."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_nonexistent_event(self, authenticated_client):
        """Test deleting non-existent event (Bad case 3)."""
        url = reverse('events:event-detail', kwargs={'pk': 99999})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ==================== REGISTER FOR EVENT TESTS ====================

@pytest.mark.django_db
class TestEventRegisterView:
    """Test suite for event registration endpoint."""
    
    def test_register_success(self, another_authenticated_client, event):
        """Test successful event registration (Good case)."""
        url = reverse('events:event-register', kwargs={'pk': event.id})
        response = another_authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'message' in response.data
        
        # Verify participation was created
        assert EventParticipant.objects.filter(
            event=event,
            user=another_authenticated_client.handler._force_user
        ).exists()
    
    def test_register_own_event(self, authenticated_client, event):
        """Test registering for own event (Bad case 1)."""
        url = reverse('events:event-register', kwargs={'pk': event.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'own event' in response.data['error'].lower()
    
    def test_register_already_registered(self, another_authenticated_client, event, another_user):
        """Test registering when already registered (Bad case 2)."""
        # First registration
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        url = reverse('events:event-register', kwargs={'pk': event.id})
        response = another_authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already registered' in response.data['error'].lower()
    
    def test_register_full_event(self, another_authenticated_client, full_event):
        """Test registering for full event (Bad case 3)."""
        url = reverse('events:event-register', kwargs={'pk': full_event.id})
        response = another_authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'capacity' in response.data['error'].lower()


# ==================== UNREGISTER FROM EVENT TESTS ====================

@pytest.mark.django_db
class TestEventUnregisterView:
    """Test suite for event unregistration endpoint."""
    
    def test_unregister_success(self, another_authenticated_client, event, another_user):
        """Test successful event unregistration (Good case)."""
        # First register
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        url = reverse('events:event-unregister', kwargs={'pk': event.id})
        response = another_authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Verify participation was deleted
        assert not EventParticipant.objects.filter(
            event=event,
            user=another_user
        ).exists()
    
    def test_unregister_not_registered(self, another_authenticated_client, event):
        """Test unregistering when not registered (Bad case 1)."""
        url = reverse('events:event-unregister', kwargs={'pk': event.id})
        response = another_authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'not registered' in response.data['error'].lower()
    
    def test_unregister_unauthenticated(self, api_client, event):
        """Test unregistering without authentication (Bad case 2)."""
        url = reverse('events:event-unregister', kwargs={'pk': event.id})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unregister_nonexistent_event(self, another_authenticated_client):
        """Test unregistering from non-existent event (Bad case 3)."""
        url = reverse('events:event-unregister', kwargs={'pk': 99999})
        response = another_authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ==================== MY ORGANIZED EVENTS TESTS ====================

@pytest.mark.django_db
class TestMyOrganizedEventsView:
    """Test suite for my organized events endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('events:event-my-organized')
    
    def test_my_organized_success(self, authenticated_client, event, user, city):
        """Test retrieving organized events (Good case)."""
        # Create another event by the same user
        Event.objects.create(
            title='Second Event',
            description='Another event',
            date=timezone.now() + timedelta(days=14),
            organizer=user,
            city=city,
            country=city.country
        )
        
        response = authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_my_organized_empty(self, another_authenticated_client):
        """Test when user has no organized events (Bad case 1)."""
        response = another_authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
    
    def test_my_organized_unauthenticated(self, api_client):
        """Test accessing organized events without authentication (Bad case 2)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_my_organized_excludes_others(self, authenticated_client, event, another_user, city):
        """Test that only user's events are returned (Bad case 3)."""
        # Create event by another user
        Event.objects.create(
            title='Other User Event',
            description='Not my event',
            date=timezone.now() + timedelta(days=14),
            organizer=another_user,
            city=city,
            country=city.country
        )
        
        response = authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == event.title


# ==================== MY REGISTERED EVENTS TESTS ====================

@pytest.mark.django_db
class TestMyRegisteredEventsView:
    """Test suite for my registered events endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('events:event-my-registered')
    
    def test_my_registered_success(self, another_authenticated_client, event, another_user):
        """Test retrieving registered events (Good case)."""
        # Register for event
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        response = another_authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == event.title
    
    def test_my_registered_empty(self, another_authenticated_client):
        """Test when user is not registered for any events (Bad case 1)."""
        response = another_authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
    
    def test_my_registered_unauthenticated(self, api_client):
        """Test accessing registered events without authentication (Bad case 2)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_my_registered_only_accepted(self, another_authenticated_client, event, another_user):
        """Test that only accepted participations are shown (Bad case 3)."""
        from apps.participants.models import PARTICIPANT_STATUS_PENDING
        
        # Create pending participation
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_PENDING
        )
        
        response = another_authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0  # Pending not included


# ==================== CATEGORY INTEGRATION TESTS ====================

@pytest.mark.django_db
class TestEventCategoryIntegration:
    """Test suite for event-category integration."""
    
    def test_create_event_with_categories(self, authenticated_client, event_data, category, another_category):
        """Test creating event with multiple categories."""
        url = reverse('events:event-list')
        event_data['category_ids'] = [category.id, another_category.id]
        response = authenticated_client.post(url, event_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify categories in database
        created_event = Event.objects.get(title=event_data['title'])
        assert created_event.categories.count() == 2
        assert category in created_event.categories.all()
        assert another_category in created_event.categories.all()
    
    def test_create_event_without_categories(self, authenticated_client, event_data):
        """Test creating event without categories is allowed."""
        url = reverse('events:event-list')
        event_data.pop('category_ids', None)
        response = authenticated_client.post(url, event_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        created_event = Event.objects.get(title=event_data['title'])
        assert created_event.categories.count() == 0
    
    def test_create_event_with_invalid_category(self, authenticated_client, event_data):
        """Test creating event with non-existent category fails."""
        url = reverse('events:event-list')
        event_data['category_ids'] = [99999]  # Non-existent
        response = authenticated_client.post(url, event_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'category_ids' in response.data
    
    def test_update_event_categories(self, authenticated_client, event, another_category):
        """Test updating event categories."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        
        # Event already has one category, add another
        update_data = {
            'category_ids': [another_category.id]
        }
        response = authenticated_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        event.refresh_from_db()
        assert event.categories.count() == 1
        assert another_category in event.categories.all()
    
    def test_update_event_add_multiple_categories(self, authenticated_client, event, category, another_category):
        """Test adding multiple categories to existing event."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        
        update_data = {
            'category_ids': [category.id, another_category.id]
        }
        response = authenticated_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        event.refresh_from_db()
        assert event.categories.count() == 2
    
    def test_update_event_clear_categories(self, authenticated_client, event):
        """Test clearing all categories from event."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        
        update_data = {
            'category_ids': []
        }
        response = authenticated_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        event.refresh_from_db()
        assert event.categories.count() == 0
    
    def test_retrieve_event_shows_categories(self, api_client, event, another_category):
        """Test that event details include categories information."""
        event.categories.add(another_category)
        
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'categories' in response.data
        assert 'category_names' in response.data
        assert len(response.data['categories']) == 2
        assert len(response.data['category_names']) == 2
        assert 'Technology' in response.data['category_names']
        assert 'Sports' in response.data['category_names']
    
    def test_list_events_shows_categories(self, api_client, event):
        """Test that event list includes categories."""
        url = reverse('events:event-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        
        event_data = response.data['results'][0]
        assert 'categories' in event_data
        assert len(event_data['categories']) >= 1
    
    def test_event_categories_serializer_format(self, api_client, event):
        """Test that categories are properly serialized with full details."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        categories = response.data['categories']
        assert len(categories) > 0
        
        # Check category has required fields
        first_category = categories[0]
        assert 'id' in first_category
        assert 'name' in first_category
        assert 'slug' in first_category
