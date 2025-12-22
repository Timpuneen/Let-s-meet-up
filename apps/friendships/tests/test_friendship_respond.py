import pytest
from rest_framework import status

from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED


@pytest.mark.django_db
class TestFriendshipResponse:
    """Tests for responding to friend requests."""
    
    def test_accept_friend_request(self, api_client, user1, user2):
        """Test accepting a friend request."""
        friendship = Friendship.objects.create(sender=user1, receiver=user2)
        
        api_client.force_authenticate(user=user2)
        
        response = api_client.post(f'/api/friendships/{friendship.id}/respond/', {
            'action': 'accept'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        friendship.refresh_from_db()
        assert friendship.status == FRIENDSHIP_STATUS_ACCEPTED
    
    def test_reject_friend_request(self, api_client, user1, user2):
        """Test rejecting a friend request."""
        friendship = Friendship.objects.create(sender=user1, receiver=user2)
        
        api_client.force_authenticate(user=user2)
        
        response = api_client.post(f'/api/friendships/{friendship.id}/respond/', {
            'action': 'reject'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        friendship.refresh_from_db()
        assert friendship.status == 'rejected'
    
    def test_only_receiver_can_respond(self, api_client, user1, user2):
        """Test only receiver can respond to request."""
        friendship = Friendship.objects.create(sender=user1, receiver=user2)
        friendship.refresh_from_db()
        
        assert Friendship.objects.filter(pk=friendship.pk).exists()
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post(f'/api/friendships/{friendship.pk}/respond/', {
            'action': 'accept'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_cannot_respond_to_non_pending_request(self, api_client, user1, user2):
        """Test cannot respond to already processed request."""
        friendship = Friendship.objects.create(
            sender=user1,
            receiver=user2,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=user2)
        
        response = api_client.post(f'/api/friendships/{friendship.id}/respond/', {
            'action': 'accept'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST