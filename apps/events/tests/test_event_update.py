import pytest
from django.urls import reverse
from rest_framework import status

from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED


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
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        update_data = {'max_participants': 0}
        response = authenticated_client.put(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_event_categories(self, authenticated_client, event, another_category):
        """Test updating event categories."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        
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