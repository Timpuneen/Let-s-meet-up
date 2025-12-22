import pytest
from rest_framework import status

from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED


@pytest.mark.django_db
class TestFriendshipStats:
    """Tests for friendship statistics."""
    
    def test_get_stats(self, api_client, user1, user2, user3):
        """Test getting friendship statistics."""
        Friendship.objects.create(sender=user1, receiver=user2)
        
        Friendship.objects.create(
            sender=user3,
            receiver=user1,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.get('/api/friendships/stats/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['friends_count'] == 1
        assert response.data['sent']['total'] == 1
        assert response.data['sent']['pending'] == 1
        assert response.data['received']['total'] == 1
        assert response.data['received']['accepted'] == 1