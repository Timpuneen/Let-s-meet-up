import pytest
from rest_framework import status

from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_PENDING, FRIENDSHIP_STATUS_ACCEPTED


@pytest.mark.django_db
class TestFriendshipCheck:
    """Tests for checking friendship status."""
    
    def test_check_no_friendship(self, api_client, user1, user2):
        """Test checking status when no friendship exists."""
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user2.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'none'
        assert response.data['can_send_request'] is True
    
    def test_check_pending_sent(self, api_client, user1, user2):
        """Test checking pending request sent by user."""
        Friendship.objects.create(sender=user1, receiver=user2)
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user2.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == FRIENDSHIP_STATUS_PENDING
        assert response.data['can_cancel'] is True
    
    def test_check_pending_received(self, api_client, user1, user2):
        """Test checking pending request received by user."""
        Friendship.objects.create(sender=user2, receiver=user1)
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user2.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == FRIENDSHIP_STATUS_PENDING
        assert response.data['can_respond'] is True
    
    def test_check_accepted(self, api_client, user1, user2):
        """Test checking accepted friendship."""
        Friendship.objects.create(
            sender=user1,
            receiver=user2,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user2.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == FRIENDSHIP_STATUS_ACCEPTED
        assert response.data['can_unfriend'] is True
    
    def test_check_self(self, api_client, user1):
        """Test checking with own email."""
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user1.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'self'