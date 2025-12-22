import pytest
from rest_framework import status

from apps.users.models import User
from apps.participants.models import EventParticipant
from apps.invitations.models import EventInvitation


@pytest.mark.django_db
class TestInvitationResponse:
    """Tests for responding to invitations."""
    
    def test_accept_invitation(self, api_client, organizer, event, invitee):
        """Test accepting an invitation."""
        invitation = EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer
        )
        
        api_client.force_authenticate(user=invitee)
        
        response = api_client.post(f'/api/invitations/{invitation.id}/respond/', {
            'action': 'accept'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        invitation.refresh_from_db()
        assert invitation.status == 'accepted'
        
        assert EventParticipant.objects.filter(
            event=event,
            user=invitee
        ).exists()
    
    def test_reject_invitation(self, api_client, organizer, event, invitee):
        """Test rejecting an invitation."""
        invitation = EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer
        )
        
        api_client.force_authenticate(user=invitee)
        
        response = api_client.post(f'/api/invitations/{invitation.id}/respond/', {
            'action': 'reject'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        invitation.refresh_from_db()
        assert invitation.status == 'rejected'
        
        assert not EventParticipant.objects.filter(
            event=event,
            user=invitee
        ).exists()
    
    def test_only_invited_user_can_respond(self, api_client, organizer, event, invitee):
        """Test that only invited user can respond."""
        invitation = EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer
        )
        
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post(f'/api/invitations/{invitation.id}/respond/', {
            'action': 'accept'
        })
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_cannot_respond_to_non_pending_invitation(
        self, api_client, organizer, event, invitee
    ):
        """Test cannot respond to already processed invitation."""
        invitation = EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer,
            status='accepted'
        )
        
        api_client.force_authenticate(user=invitee)
        
        response = api_client.post(f'/api/invitations/{invitation.id}/respond/', {
            'action': 'accept'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_accept_when_event_full(self, api_client, organizer, event, invitee):
        """Test cannot accept invitation when event is full."""
        event.max_participants = 1
        event.save()
        
        other_user = User.objects.create_user(
            email='other@test.com',
            name='Other',
            password='testpass123'
        )
        EventParticipant.objects.create(event=event, user=other_user)
        
        invitation = EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer
        )
        
        api_client.force_authenticate(user=invitee)
        
        response = api_client.post(f'/api/invitations/{invitation.id}/respond/', {
            'action': 'accept'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST