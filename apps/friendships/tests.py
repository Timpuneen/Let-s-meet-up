"""
Tests for Friendships.

This module contains comprehensive tests for friendship functionality
including permissions, validation, and workflow.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_PENDING, FRIENDSHIP_STATUS_ACCEPTED


@pytest.fixture
def api_client():
    """Fixture providing API client."""
    return APIClient()


@pytest.fixture
def user1(db):
    """Fixture providing first test user."""
    return User.objects.create_user(
        email='user1@test.com',
        name='User One',
        password='testpass123'
    )


@pytest.fixture
def user2(db):
    """Fixture providing second test user."""
    return User.objects.create_user(
        email='user2@test.com',
        name='User Two',
        password='testpass123'
    )


@pytest.fixture
def user3(db):
    """Fixture providing third test user."""
    return User.objects.create_user(
        email='user3@test.com',
        name='User Three',
        password='testpass123'
    )


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
        
        # Debug: check if friendship exists
        assert Friendship.objects.filter(pk=friendship.pk).exists()
        print(f"DEBUG: Friendship ID = {friendship.pk}, exists in DB")
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post(f'/api/friendships/{friendship.pk}/respond/', {
            'action': 'accept'
        })
        
        print(f"DEBUG: Response status = {response.status_code}")
        if response.status_code == 404:
            print(f"DEBUG: Response data = {response.data}")
        
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


@pytest.mark.django_db
class TestFriendshipDeletion:
    """Tests for removing friendships."""
    
    def test_sender_can_cancel_pending_request(self, api_client, user1, user2):
        """Test sender can cancel their pending request."""
        friendship = Friendship.objects.create(sender=user1, receiver=user2)
        friendship.refresh_from_db()  # Ensure we have the correct ID
        
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


@pytest.mark.django_db
class TestFriendshipStats:
    """Tests for friendship statistics."""
    
    def test_get_stats(self, api_client, user1, user2, user3):
        """Test getting friendship statistics."""
        # User1 sends request to user2 (pending)
        Friendship.objects.create(sender=user1, receiver=user2)
        
        # User3 sends request to user1 (accepted)
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


@pytest.mark.django_db
class TestFriendshipCheck:
    """Tests for checking friendship status."""
    
    def test_check_no_friendship(self, api_client, user1, user2):
        """Test checking status when no friendship exists."""
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user2.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'none'
        assert response.data['can_send_request'] is True
    
    def test_check_pending_sent(self, api_client, user1, user2):
        """Test checking pending request sent by user."""
        Friendship.objects.create(sender=user1, receiver=user2)
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user2.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == FRIENDSHIP_STATUS_PENDING
        assert response.data['can_cancel'] is True
    
    def test_check_pending_received(self, api_client, user1, user2):
        """Test checking pending request received by user."""
        Friendship.objects.create(sender=user2, receiver=user1)
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user2.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == FRIENDSHIP_STATUS_PENDING
        assert response.data['can_respond'] is True
    
    def test_check_accepted(self, api_client, user1, user2):
        """Test checking accepted friendship."""
        Friendship.objects.create(
            sender=user1,
            receiver=user2,
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user2.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == FRIENDSHIP_STATUS_ACCEPTED
        assert response.data['can_unfriend'] is True
    
    def test_check_self(self, api_client, user1):
        """Test checking with own email."""
        api_client.force_authenticate(user=user1)
        
        response = api_client.post('/api/friendships/check/', {
            'user_email': user1.email
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'self'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])