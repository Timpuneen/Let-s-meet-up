import pytest
from rest_framework import status

from apps.invitations.models import EventInvitation, INVITATION_STATUS_PENDING


@pytest.mark.django_db
class TestInvitationListing:
    """Tests for listing invitations."""
    
    def test_list_received_invitations(self, api_client, organizer, event, invitee):
        """Test listing invitations received by user."""
        EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer
        )
        
        api_client.force_authenticate(user=invitee)
        
        response = api_client.get('/api/invitations/?type=received')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_list_sent_invitations(self, api_client, organizer, event, invitee):
        """Test listing invitations sent by user."""
        EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer
        )
        
        api_client.force_authenticate(user=organizer)
        
        response = api_client.get('/api/invitations/?type=sent')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_filter_by_status(self, api_client, organizer, event, invitee):
        """Test filtering invitations by status."""
        EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer,
            status=INVITATION_STATUS_PENDING
        )
        
        api_client.force_authenticate(user=invitee)
        
        response = api_client.get('/api/invitations/?status=pending')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_invitation_stats(self, api_client, organizer, event, invitee):
        """Test getting invitation statistics."""
        EventInvitation.objects.create(
            event=event,
            invited_user=invitee,
            invited_by=organizer,
            status=INVITATION_STATUS_PENDING
        )
        
        api_client.force_authenticate(user=invitee)
        
        response = api_client.get('/api/invitations/stats/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['received']['total'] == 1
        assert response.data['received']['pending'] == 1