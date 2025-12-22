import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.events.models import Event
from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED


@pytest.mark.django_db
class TestMyOrganizedEventsView:
    """Test suite for my organized events endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('events:event-my-organized')
    
    def test_my_organized_success(self, authenticated_client, event, user, city):
        """Test retrieving organized events (Good case)."""
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


@pytest.mark.django_db
class TestMyRegisteredEventsView:
    """Test suite for my registered events endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('events:event-my-registered')
    
    def test_my_registered_success(self, another_authenticated_client, event, another_user):
        """Test retrieving registered events (Good case)."""
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