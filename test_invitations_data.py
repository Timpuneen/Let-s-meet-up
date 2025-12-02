from django.utils import timezone
from datetime import timedelta
from apps.users.models import User, INVITATION_PRIVACY_EVERYONE, INVITATION_PRIVACY_FRIENDS
from apps.events.models import Event, INVITATION_PERM_PARTICIPANTS
from apps.participants.models import EventParticipant
from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED

# Создать пользователей
organizer = User.objects.create_user(
    email='organizer@test.com',
    name='Event Organizer',
    password='password123'
)

participant = User.objects.create_user(
    email='participant@test.com',
    name='Participant User',
    password='password123'
)

invitee = User.objects.create_user(
    email='invitee@test.com',
    name='Invitee User',
    password='password123',
    invitation_privacy=INVITATION_PRIVACY_EVERYONE
)

friend = User.objects.create_user(
    email='friend@test.com',
    name='Friend User',
    password='password123',
    invitation_privacy=INVITATION_PRIVACY_FRIENDS
)

# Создать дружбу
Friendship.objects.create(
    sender=organizer,
    receiver=friend,
    status=FRIENDSHIP_STATUS_ACCEPTED
)

# Создать событие
event = Event.objects.create(
    title='Test Meetup Event',
    description='Come join us for a test event!',
    address='Test Address, 123',
    date=timezone.now() + timedelta(days=7),
    organizer=organizer,
    invitation_perm=INVITATION_PERM_PARTICIPANTS,
    max_participants=20
)

# Добавить участника
EventParticipant.objects.create(
    event=event,
    user=participant,
    is_admin=False
)

print("✅ Test data created successfully!")
print(f"Organizer: {organizer.email}")
print(f"Participant: {participant.email}")
print(f"Invitee: {invitee.email}")
print(f"Friend: {friend.email}")
print(f"Event: {event.title} (ID: {event.id})")