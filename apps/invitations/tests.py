import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User, INVITATION_PRIVACY_EVERYONE, INVITATION_PRIVACY_FRIENDS, INVITATION_PRIVACY_NONE
from apps.events.models import Event, INVITATION_PERM_ORGANIZER, INVITATION_PERM_ADMINS, INVITATION_PERM_PARTICIPANTS
from apps.participants.models import EventParticipant
from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED
from apps.invitations.models import EventInvitation, INVITATION_STATUS_PENDING


@pytest.fixture
def api_client():
    """Fixture providing API client."""
    return APIClient()


@pytest.fixture
def organizer(db):
    """Fixture providing event organizer user."""
    return User.objects.create_user(
        email='organizer@test.com',
        name='Organizer',
        password='testpass123'
    )


@pytest.fixture
def participant(db):
    """Fixture providing participant user."""
    return User.objects.create_user(
        email='participant@test.com',
        name='Participant',
        password='testpass123'
    )


@pytest.fixture
def admin_participant(db):
    """Fixture providing admin participant user."""
    return User.objects.create_user(
        email='admin@test.com',
        name='Admin',
        password='testpass123'
    )


@pytest.fixture
def invitee(db):
    """Fixture providing user to be invited."""
    return User.objects.create_user(
        email='invitee@test.com',
        name='Invitee',
        password='testpass123',
        invitation_privacy=INVITATION_PRIVACY_EVERYONE
    )


@pytest.fixture
def event(db, organizer):
    """Fixture providing a test event."""
    return Event.objects.create(
        title='Test Event',
        description='Test Description',
        date=timezone.now() + timedelta(days=7),
        organizer=organizer,
        invitation_perm=INVITATION_PERM_PARTICIPANTS,
        max_participants=10
    )


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