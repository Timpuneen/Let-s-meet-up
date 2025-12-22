import pytest
from django.urls import reverse
from rest_framework import status

from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED


@pytest.mark.django_db
class TestEventRegisterView:
    """Test suite for event registration endpoint."""
    
    def test_register_success(self, another_authenticated_client, event):
        """Test successful event registration (Good case)."""
        url = reverse('events:event-register', kwargs={'pk': event.id})
        response = another_authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'message' in response.data
        
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


@pytest.mark.django_db
class TestEventUnregisterView:
    """Test suite for event unregistration endpoint."""
    
    def test_unregister_success(self, another_authenticated_client, event, another_user):
        """Test successful event unregistration (Good case)."""
        EventParticipant.objects.create(
            event=event,
            user=another_user,
            status=PARTICIPANT_STATUS_ACCEPTED
        )
        
        url = reverse('events:event-unregister', kwargs={'pk': event.id})
        response = another_authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
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