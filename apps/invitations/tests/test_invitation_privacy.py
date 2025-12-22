import pytest
from rest_framework import status

from apps.users.models import INVITATION_PRIVACY_EVERYONE, INVITATION_PRIVACY_FRIENDS, INVITATION_PRIVACY_NONE
from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED


@pytest.mark.django_db
class TestInvitationPrivacy:
    """Tests for invitation privacy settings."""
    
    def test_can_invite_user_with_everyone_privacy(self, api_client, organizer, event, invitee):
        """Test inviting user with 'everyone' privacy."""
        invitee.invitation_privacy = INVITATION_PRIVACY_EVERYONE
        invitee.save()
        
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_can_invite_friend_with_friends_privacy(self, api_client, organizer, event, invitee):
        """Test inviting friend with 'friends only' privacy."""
        invitee.invitation_privacy = INVITATION_PRIVACY_FRIENDS
        invitee.save()
        
        Friendship.objects.create(
            sender=organizer,
            receiver=invitee,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_cannot_invite_non_friend_with_friends_privacy(
        self, api_client, organizer, event, invitee
    ):
        """Test cannot invite non-friend with 'friends only' privacy."""
        invitee.invitation_privacy = INVITATION_PRIVACY_FRIENDS
        invitee.save()
        
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_invite_user_with_none_privacy(self, api_client, organizer, event, invitee):
        """Test cannot invite user with 'none' privacy."""
        invitee.invitation_privacy = INVITATION_PRIVACY_NONE
        invitee.save()
        
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST