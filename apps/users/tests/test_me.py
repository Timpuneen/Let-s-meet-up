import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestMeView:
    """Test suite for current user profile endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('users:auth-me')
    
    def test_me_success(self, authenticated_client, user):
        """Test retrieving current user profile with authentication (Good case)."""
        response = authenticated_client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['name'] == user.name
        assert 'id' in response.data
        assert 'created_at' in response.data
        assert 'invitation_privacy' in response.data
    
    def test_me_unauthenticated(self, api_client):
        """Test accessing profile without authentication (Bad case 1)."""
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_me_invalid_token(self, api_client):
        """Test accessing profile with invalid token (Bad case 2)."""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_here')
        response = api_client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED