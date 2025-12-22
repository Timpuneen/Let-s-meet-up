import pytest
from rest_framework import status

from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED


@pytest.mark.django_db
class TestFriendshipDeletion:
    """Tests for removing friendships."""
    
    def test_sender_can_cancel_pending_request(self, api_client, user1, user2):
        """Test sender can cancel their pending request."""
        friendship = Friendship.objects.create(sender=user1, receiver=user2)
        friendship.refresh_from_db() 
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.delete(f'/api/friendships/{friendship.pk}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Friendship.objects.filter(pk=friendship.pk).exists()
    
    def test_receiver_can_delete_request(self, api_client, user1, user2):
        """Test receiver can delete request (alternative to reject)."""
        friendship = Friendship.objects.create(sender=user1, receiver=user2)
        
        api_client.force_authenticate(user=user2)
        
        response = api_client.delete(f'/api/friendships/{friendship.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Friendship.objects.filter(id=friendship.id).exists()
    
    def test_either_can_unfriend(self, api_client, user1, user2):
        """Test either user can remove accepted friendship."""
        friendship = Friendship.objects.create(
            sender=user1,
            receiver=user2,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=user2)
        
        response = api_client.delete(f'/api/friendships/{friendship.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Friendship.objects.filter(id=friendship.id).exists()