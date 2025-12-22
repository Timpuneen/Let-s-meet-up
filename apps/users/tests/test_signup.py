import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.models import User


@pytest.mark.django_db
class TestSignupView:
    """Test suite for user registration endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('users:auth-signup')
    
    def test_signup_success(self, api_client, user_data):
        """Test successful user registration (Good case)."""
        response = api_client.post(self.url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['email'] == user_data['email']
        assert response.data['user']['name'] == user_data['name']
        
        assert User.objects.filter(email=user_data['email']).exists()
    
    def test_signup_duplicate_email(self, api_client, user_data, user):
        """Test registration with duplicate email (Bad case 1)."""
        user_data['email'] = user.email
        response = api_client.post(self.url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_signup_password_mismatch(self, api_client, user_data):
        """Test registration with mismatched passwords (Bad case 2)."""
        user_data['password_confirm'] = 'differentpassword'
        response = api_client.post(self.url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
    
    def test_signup_short_password(self, api_client, user_data):
        """Test registration with password shorter than 6 characters (Bad case 3)."""
        user_data['password'] = '12345' 
        user_data['password_confirm'] = '12345'
        response = api_client.post(self.url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data