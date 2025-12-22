import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestLoginView:
    """Test suite for user login endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('users:auth-login')
    
    def test_login_success(self, api_client, login_data):
        """Test successful user login (Good case)."""
        response = api_client.post(self.url, login_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['email'] == login_data['email']
    
    def test_login_invalid_password(self, api_client, login_data):
        """Test login with wrong password (Bad case 1)."""
        login_data['password'] = 'wrongpassword'
        response = api_client.post(self.url, login_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent email (Bad case 2)."""
        invalid_payload = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        response = api_client.post(self.url, invalid_payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data
    
    def test_login_inactive_user(self, api_client, user, login_data):
        """Test login with deactivated account (Bad case 3)."""
        user.is_active = False
        user.save()
        
        response = api_client.post(self.url, login_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data