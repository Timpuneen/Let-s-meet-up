import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from apps.events.models import Event
from apps.geography.models import Country, City
from .models import EventComment


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Fixture for regular authenticated user."""
    return User.objects.create_user(
        email='user@example.com',
        password='testpass123',
        name='Test User'
    )


@pytest.fixture
def another_user(db):
    """Fixture for another regular user."""
    return User.objects.create_user(
        email='another@example.com',
        password='testpass123',
        name='Another User'
    )


@pytest.fixture
def admin_user(db):
    """Fixture for admin user."""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        name='Admin User'
    )


@pytest.fixture
def country(db):
    """Fixture for a test country."""
    return Country.objects.create(
        name='Test Country',
        code='TC'
    )


@pytest.fixture
def city(db, country):
    """Fixture for a test city."""
    return City.objects.create(
        name='Test City',
        country=country
    )


@pytest.fixture
def event(db, user, country, city):
    """Fixture for a test event."""
    from datetime import datetime, timedelta
    return Event.objects.create(
        title='Test Event',
        description='Test event description',
        address='123 Test Street',
        date=datetime.now() + timedelta(days=7),
        organizer=user,
        country=country,
        city=city
    )


@pytest.fixture
def comment(db, event, user):
    """Fixture for a test comment."""
    return EventComment.objects.create(
        event=event,
        user=user,
        content='This is a test comment'
    )


@pytest.fixture
def comments(db, event, user, another_user):
    """Fixture for multiple test comments."""
    return [
        EventComment.objects.create(
            event=event,
            user=user,
            content='First comment'
        ),
        EventComment.objects.create(
            event=event,
            user=another_user,
            content='Second comment'
        ),
        EventComment.objects.create(
            event=event,
            user=user,
            content='Third comment'
        ),
    ]


@pytest.mark.django_db
class TestCommentListView:
    """Tests for listing comments (GET /api/comments/)."""

    def test_list_comments_success(self, api_client, user, comments):
        """Test successful retrieval of comment list."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3

    def test_list_comments_unauthenticated(self, api_client, comments):
        """Test that unauthenticated users cannot list comments."""
        url = reverse('comments:comment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_comments_filter_by_event(self, api_client, user, event, another_user, country, city):
        """Test filtering comments by event."""
        from datetime import datetime, timedelta
        
        another_event = Event.objects.create(
            title='Another Event',
            description='Another event description',
            address='456 Test Street',
            date=datetime.now() + timedelta(days=14),
            organizer=another_user,
            country=country,
            city=city
        )
        
        EventComment.objects.create(event=event, user=user, content='Comment on event 1')
        EventComment.objects.create(event=event, user=user, content='Another comment on event 1')
        EventComment.objects.create(event=another_event, user=user, content='Comment on event 2')
        
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url, {'event': event.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        for comment in response.data['results']:
            assert comment['event'] == event.id

    def test_list_comments_filter_by_user(self, api_client, user, comments):
        """Test filtering comments by user."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url, {'user': user.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        for comment in response.data['results']:
            assert comment['user']['id'] == user.id

    def test_list_comments_empty(self, api_client, user):
        """Test listing when no comments exist."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_list_comments_pagination(self, api_client, user, event):
        """Test that comments are paginated."""
        for i in range(25):
            EventComment.objects.create(
                event=event,
                user=user,
                content=f'Comment {i}'
            )
        
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20 


@pytest.mark.django_db
class TestCommentRetrieveView:
    """Tests for retrieving comment details (GET /api/comments/{id}/)."""

    def test_retrieve_comment_success(self, api_client, user, comment):
        """Test successful retrieval of comment details."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == comment.id
        assert response.data['content'] == 'This is a test comment'
        assert 'user' in response.data
        assert 'depth' in response.data
        assert 'reply_count' in response.data

    def test_retrieve_comment_not_found(self, api_client, user):
        """Test retrieving a non-existent comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': 9999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_comment_unauthenticated(self, api_client, comment):
        """Test that unauthenticated users cannot retrieve comments."""
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCommentCreateView:
    """Tests for creating comments (POST /api/comments/)."""

    def test_create_comment_success(self, api_client, user, event):
        """Test successful comment creation by authenticated user."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'event': event.id,
            'content': 'This is a new comment'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'This is a new comment'
        assert response.data['user']['id'] == user.id
        assert response.data['event'] == event.id
        assert EventComment.objects.filter(content='This is a new comment').exists()

    def test_create_comment_reply_success(self, api_client, user, comment):
        """Test successful creation of a reply to a comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'event': comment.event.id,
            'parent': comment.id,
            'content': 'This is a reply'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['parent'] == comment.id
        assert response.data['content'] == 'This is a reply'
        assert response.data['depth'] == 1

    def test_create_comment_unauthenticated(self, api_client, event):
        """Test that unauthenticated users cannot create comments."""
        url = reverse('comments:comment-list')
        data = {
            'event': event.id,
            'content': 'Should not be created'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_comment_missing_content(self, api_client, user, event):
        """Test creating comment without required content field."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'event': event.id
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data

    def test_create_comment_missing_event(self, api_client, user):
        """Test creating comment without required event field."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'content': 'Test comment'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'event' in response.data

    def test_create_comment_invalid_parent_event(self, api_client, user, event, another_user, country, city):
        """Test creating reply with parent from different event."""
        from datetime import datetime, timedelta
        
        another_event = Event.objects.create(
            title='Another Event',
            description='Description',
            date=datetime.now() + timedelta(days=7),
            organizer=another_user,
            country=country,
            city=city
        )
        another_comment = EventComment.objects.create(
            event=another_event,
            user=another_user,
            content='Comment on another event'
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-list')
        data = {
            'event': event.id,
            'parent': another_comment.id,
            'content': 'This should fail'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'parent' in response.data


@pytest.mark.django_db
class TestCommentUpdateView:
    """Tests for updating comments (PUT/PATCH /api/comments/{id}/)."""

    def test_update_comment_success_by_owner(self, api_client, user, comment):
        """Test successful comment update by owner."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        data = {
            'content': 'Updated comment content'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Updated comment content'
        
        comment.refresh_from_db()
        assert comment.content == 'Updated comment content'

    def test_update_comment_success_by_admin(self, api_client, admin_user, comment):
        """Test successful comment update by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        data = {
            'content': 'Admin updated content'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Admin updated content'

    def test_update_comment_forbidden_by_other_user(self, api_client, another_user, comment):
        """Test that other users cannot update comments they don't own."""
        api_client.force_authenticate(user=another_user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        data = {
            'content': 'Should not update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        comment.refresh_from_db()
        assert comment.content == 'This is a test comment'

    def test_update_comment_unauthenticated(self, api_client, comment):
        """Test that unauthenticated users cannot update comments."""
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        data = {
            'content': 'Should not update'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_comment_not_found(self, api_client, user):
        """Test updating a non-existent comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': 9999})
        data = {
            'content': 'Does not exist'
        }
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCommentDeleteView:
    """Tests for deleting comments (DELETE /api/comments/{id}/)."""

    def test_delete_comment_success_by_owner(self, api_client, user, comment):
        """Test successful comment deletion by owner."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        comment.refresh_from_db()
        assert comment.is_deleted

    def test_delete_comment_success_by_admin(self, api_client, admin_user, comment):
        """Test successful comment deletion by admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        comment.refresh_from_db()
        assert comment.is_deleted

    def test_delete_comment_forbidden_by_other_user(self, api_client, another_user, comment):
        """Test that other users cannot delete comments they don't own."""
        api_client.force_authenticate(user=another_user)
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        comment.refresh_from_db()
        assert not comment.is_deleted

    def test_delete_comment_unauthenticated(self, api_client, comment):
        """Test that unauthenticated users cannot delete comments."""
        url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        comment.refresh_from_db()
        assert not comment.is_deleted

    def test_delete_comment_not_found(self, api_client, user):
        """Test deleting a non-existent comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-detail', kwargs={'pk': 9999})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCommentRepliesView:
    """Tests for nested replies endpoint (GET /api/comments/{id}/replies/)."""

    def test_get_replies_success(self, api_client, user, comment, another_user):
        """Test successful retrieval of nested replies."""
        reply1 = EventComment.objects.create(
            event=comment.event,
            user=user,
            parent=comment,
            content='First reply'
        )
        reply2 = EventComment.objects.create(
            event=comment.event,
            user=another_user,
            parent=comment,
            content='Second reply'
        )
        EventComment.objects.create(
            event=comment.event,
            user=user,
            parent=reply1,
            content='Nested reply'
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-replies', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        first_reply = next(r for r in response.data if r['content'] == 'First reply')
        assert len(first_reply['replies']) == 1
        assert first_reply['replies'][0]['content'] == 'Nested reply'

    def test_get_replies_empty(self, api_client, user, comment):
        """Test getting replies when there are none."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-replies', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_get_replies_unauthenticated(self, api_client, comment):
        """Test that unauthenticated users cannot get replies."""
        url = reverse('comments:comment-replies', kwargs={'pk': comment.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_replies_not_found(self, api_client, user):
        """Test getting replies for non-existent comment."""
        api_client.force_authenticate(user=user)
        url = reverse('comments:comment-replies', kwargs={'pk': 9999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCommentPermissions:
    """Comprehensive tests for comment permissions."""

    def test_authenticated_user_can_create_and_read(self, api_client, user, event, comment):
        """Test that authenticated users can create and read comments."""
        api_client.force_authenticate(user=user)
        
        list_url = reverse('comments:comment-list')
        detail_url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(
            list_url,
            {'event': event.id, 'content': 'New comment'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_owner_can_update_and_delete_own_comments(self, api_client, user, comment):
        """Test that comment owners can update and delete their own comments."""
        api_client.force_authenticate(user=user)
        detail_url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})

        response = api_client.patch(
            detail_url,
            {'content': 'Updated content'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_other_users_cannot_update_or_delete(self, api_client, another_user, comment):
        """Test that users cannot update or delete comments they don't own."""
        api_client.force_authenticate(user=another_user)
        detail_url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})

        response = api_client.patch(
            detail_url,
            {'content': 'Should not update'},
            format='json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_has_full_access(self, api_client, admin_user, user, event, comment):
        """Test that admin users have full CRUD access to all comments."""
        api_client.force_authenticate(user=admin_user)
        
        list_url = reverse('comments:comment-list')
        detail_url = reverse('comments:comment-detail', kwargs={'pk': comment.pk})

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        response = api_client.post(
            list_url,
            {'event': event.id, 'content': 'Admin comment'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = api_client.patch(
            detail_url,
            {'content': 'Admin updated'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

