import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestEventDeleteView:
    """Test suite for event deletion endpoint."""
    
    def test_delete_event_success(self, authenticated_client, event):
        """Test successful event deletion by organizer (Good case)."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
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