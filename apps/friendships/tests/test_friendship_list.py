import pytest
from rest_framework import status

from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_PENDING, FRIENDSHIP_STATUS_ACCEPTED


@pytest.mark.django_db
class TestFriendshipListing:
    """Tests for listing friendships."""
    
    def test_list_received_requests(self, api_client, user1, user2, user3):
        """Test listing friend requests received by user."""
        Friendship.objects.create(sender=user1, receiver=user2)
        Friendship.objects.create(sender=user3, receiver=user2)
        
        api_client.force_authenticate(user=user2)
        
        response = api_client.get('/api/friendships/?type=received')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_list_sent_requests(self, api_client, user1, user2, user3):
        """Test listing friend requests sent by user."""
        Friendship.objects.create(sender=user1, receiver=user2)
        Friendship.objects.create(sender=user1, receiver=user3)
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.get('/api/friendships/?type=sent')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_filter_by_status(self, api_client, user1, user2, user3):
        """Test filtering friendships by status."""
        Friendship.objects.create(
            sender=user1,
            receiver=user2,
            status=FRIENDSHIP_STATUS_PENDING
        )
        Friendship.objects.create(
            sender=user3,
            receiver=user2,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=user2)
        
        response = api_client.get('/api/friendships/?type=received&status=pending')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_get_pending_requests(self, api_client, user1, user2):
        """Test getting only pending requests."""
        Friendship.objects.create(sender=user1, receiver=user2)
        
        api_client.force_authenticate(user=user2)
        
        response = api_client.get('/api/friendships/pending/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_get_friends_list(self, api_client, user1, user2, user3):
        """Test getting list of friends."""
        Friendship.objects.create(
            sender=user1,
            receiver=user2,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        Friendship.objects.create(
            sender=user3,
            receiver=user1,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.get('/api/friendships/friends/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2