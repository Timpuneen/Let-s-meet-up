import pytest
from django.urls import reverse
from rest_framework import status


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
        event.delete()
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
    
    def test_event_categories_serializer_format(self, api_client, event):
        """Test that categories are properly serialized with full details."""
        url = reverse('events:event-detail', kwargs={'pk': event.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        categories = response.data['categories']
        assert len(categories) > 0
        
        first_category = categories[0]
        assert 'id' in first_category
        assert 'name' in first_category
        assert 'slug' in first_category