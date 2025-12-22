import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestTokenRefreshView:
    """Test suite for JWT token refresh endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data and URLs."""
        self.url = reverse('users:token_refresh')
    
    def test_token_refresh_success(self, api_client, user):
        """Test successful token refresh (Good case)."""
        refresh = RefreshToken.for_user(user)
        response = api_client.post(
            self.url,
            {'refresh': str(refresh)},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert response.data['access'] is not None
    
    def test_token_refresh_invalid_token(self, api_client):
        """Test refresh with invalid token (Bad case 1)."""
        response = api_client.post(
            self.url,
            {'refresh': 'invalid_refresh_token'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_refresh_missing_token(self, api_client):
        """Test refresh without providing token (Bad case 2)."""
        response = api_client.post(self.url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_token_refresh_access_token_instead(self, api_client, user):
        """Test refresh with access token instead of refresh token (Bad case 3)."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response = api_client.post(
            self.url,
            {'refresh': access_token},
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED