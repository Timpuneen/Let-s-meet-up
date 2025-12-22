import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.events.models import Event


@pytest.mark.django_db
class TestEventListView:
    """Test suite for event listing endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('events:event-list')
    
    def test_list_events_success(self, api_client, event):
        """Test listing events returns only upcoming events (Good case)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == event.title
    
    def test_list_events_empty(self, api_client):
        """Test listing when no events exist (Bad case 1)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
    
    def test_list_events_pagination(self, api_client, user, city):
        """Test pagination works correctly (Bad case 2)."""
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
    
    def test_list_events_shows_categories(self, api_client, event):
        """Test that event list includes categories."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        
        event_data = response.data['results'][0]
        assert 'categories' in event_data
        assert len(event_data['categories']) >= 1