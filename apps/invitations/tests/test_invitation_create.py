import pytest
from rest_framework import status

from apps.events.models import INVITATION_PERM_ADMINS
from apps.participants.models import EventParticipant
from apps.invitations.models import EventInvitation


@pytest.mark.django_db
class TestEventInvitationCreation:
    """Tests for creating event invitations."""
    
    def test_organizer_can_invite(self, api_client, organizer, event, invitee):
        """Test that organizer can invite users."""
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert EventInvitation.objects.filter(
            event=event,
            invited_user=invitee,
            invited_by=organizer
        ).exists()
    
    def test_participant_can_invite_when_allowed(self, api_client, participant, event, invitee):
        """Test that participant can invite when event allows it."""
        EventParticipant.objects.create(event=event, user=participant)
        
        api_client.force_authenticate(user=participant)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_admin_can_invite_when_admins_only(self, api_client, admin_participant, event, invitee):
        """Test that admin can invite when only admins are allowed."""
        event.invitation_perm = INVITATION_PERM_ADMINS
        event.save()
        
        EventParticipant.objects.create(event=event, user=admin_participant, is_admin=True)
        
        api_client.force_authenticate(user=admin_participant)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_regular_participant_cannot_invite_when_admins_only(
        self, api_client, participant, event, invitee
    ):
        """Test that regular participant cannot invite when only admins allowed."""
        event.invitation_perm = INVITATION_PERM_ADMINS
        event.save()
        
        EventParticipant.objects.create(event=event, user=participant, is_admin=False)
        
        api_client.force_authenticate(user=participant)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_non_participant_cannot_invite(self, api_client, participant, event, invitee):
        """Test that non-participant cannot invite."""
        api_client.force_authenticate(user=participant)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_invite_organizer(self, api_client, organizer, event):
        """Test that cannot invite the organizer."""
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': organizer.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_invite_existing_participant(self, api_client, organizer, event, invitee):
        """Test that cannot invite existing participant."""
        EventParticipant.objects.create(event=event, user=invitee)
        
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cannot_create_duplicate_invitation(self, api_client, organizer, event, invitee):
        """Test that cannot create duplicate invitation."""
        EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer
        )
        
        api_client.force_authenticate(user=organizer)
        
        response = api_client.post('/api/invitations/', {
            'event': event.id,
            'invited_user_email': invitee.email
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST