import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.events.models import Event


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
        other_country = country.__class__.objects.create(name='Russia', code='RU')
        event_data['country'] = other_country.id
        
        response = authenticated_client.post(self.url, event_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_event_with_categories(self, authenticated_client, event_data, category, another_category):
        """Test creating event with multiple categories."""
        event_data['category_ids'] = [category.id, another_category.id]
        response = authenticated_client.post(self.url, event_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        created_event = Event.objects.get(title=event_data['title'])
        assert created_event.categories.count() == 2
        assert category in created_event.categories.all()
        assert another_category in created_event.categories.all()
    
    def test_create_event_without_categories(self, authenticated_client, event_data):
        """Test creating event without categories is allowed."""
        event_data.pop('category_ids', None)
        response = authenticated_client.post(self.url, event_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        created_event = Event.objects.get(title=event_data['title'])
        assert created_event.categories.count() == 0
    
    def test_create_event_with_invalid_category(self, authenticated_client, event_data):
        """Test creating event with non-existent category fails."""
        event_data['category_ids'] = [99999]
        response = authenticated_client.post(self.url, event_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'category_ids' in response.data