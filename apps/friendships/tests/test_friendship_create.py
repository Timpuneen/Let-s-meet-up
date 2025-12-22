import pytest
from rest_framework import status

from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_PENDING


@pytest.mark.django_db
class TestFriendshipCreation:
    """Tests for creating friend requests."""
    
    def test_send_friend_request(self, api_client, user1, user2):
        """Test sending a friend request."""
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/', {
            'receiver_email': user2.email
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Friendship.objects.filter(
            sender=user1,
            receiver=user2,
            status=FRIENDSHIP_STATUS_PENDING
        ).exists()
    
    def test_cannot_send_request_to_self(self, api_client, user1):
        """Test cannot send friend request to yourself."""
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/', {
            'receiver_email': user1.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_send_duplicate_request(self, api_client, user1, user2):
        """Test cannot send duplicate friend request."""
        Friendship.objects.create(sender=user1, receiver=user2)
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/', {
            'receiver_email': user2.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_send_request_if_received_from_user(self, api_client, user1, user2):
        """Test cannot send request if already received from that user."""
        Friendship.objects.create(sender=user2, receiver=user1)
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/', {
            'receiver_email': user2.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already sent you' in str(response.data).lower()
    
    def test_cannot_send_request_to_nonexistent_user(self, api_client, user1):
        """Test cannot send request to non-existent user."""
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/', {
            'receiver_email': 'nonexistent@test.com'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_can_resend_after_rejection(self, api_client, user1, user2):
        """Test can send new request after previous rejection."""
        Friendship.objects.create(
            sender=user1,
            receiver=user2,
            status='rejected'
        )
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/', {
            'receiver_email': user2.email
        })
        
        assert response.status_code == status.HTTP_201_CREATED