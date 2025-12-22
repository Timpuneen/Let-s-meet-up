"""
Seeder command for invitations app.

Seeds the database with event invitations.
"""

from typing import Any, List, Set
import random

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.core.utils.seeding import random_sample, random_choice, weighted_choice
from apps.invitations.models import EventInvitation, INVITATION_STATUS_PENDING, INVITATION_STATUS_ACCEPTED, INVITATION_STATUS_REJECTED
from apps.events.models import Event, INVITATION_PERM_ORGANIZER, INVITATION_PERM_ADMINS, INVITATION_PERM_PARTICIPANTS
from apps.participants.models import EventParticipant
from apps.users.models import User


DEFAULT_MIN_INVITATIONS: int = 2
DEFAULT_MAX_INVITATIONS: int = 8


class Command(BaseSeederCommand):
    """
    Seed event invitation data.

    Creates invitations for events with varied statuses.
    Depends on: Events, Users, Participants.
    """

    help = 'Seed event invitations'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--min',
            type=int,
            default=DEFAULT_MIN_INVITATIONS,
            help=f'Minimum invitations per event (default: {DEFAULT_MIN_INVITATIONS})',
        )
        parser.add_argument(
            '--max',
            type=int,
            default=DEFAULT_MAX_INVITATIONS,
            help=f'Maximum invitations per event (default: {DEFAULT_MAX_INVITATIONS})',
        )

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Invitations'

    def seed_data(self, **options: Any) -> int:
        """
        Seed invitations.

        Args:
            **options: Command options.

        Returns:
            Number of invitations created.
        """
        self.check_dependencies({
            'Event': Event,
            'User': User,
            'EventParticipant': EventParticipant,
        })

        min_invitations: int = options.get('min', DEFAULT_MIN_INVITATIONS)
        max_invitations: int = options.get('max', DEFAULT_MAX_INVITATIONS)

        invitations_created = self._create_invitations(min_invitations, max_invitations)
        return invitations_created

    def clear_data(self) -> None:
        """Clear all invitations."""
        EventInvitation.objects.all().delete()

    def _create_invitations(self, min_count: int, max_count: int) -> int:
        """
        Create invitations for events.

        Args:
            min_count: Minimum invitations per event.
            max_count: Maximum invitations per event.

        Returns:
            Total number of invitations created.
        """
        events: List[Event] = list(Event.objects.all())
        users: List[User] = list(User.objects.all())

        if not events or not users:
            self.stdout.write(self.style.ERROR('Missing required data'))
            return 0

        created_count: int = 0

        statuses: List[str] = [
            INVITATION_STATUS_PENDING
        ] * 60 + [INVITATION_STATUS_ACCEPTED] * 25 + [INVITATION_STATUS_REJECTED] * 15

        for event in events:
            existing_participant_ids: Set[int] = set(
                EventParticipant.objects.filter(event=event).values_list('user_id', flat=True)
            )
            existing_participant_ids.add(event.organizer_id)

            potential_inviters: List[User] = [event.organizer]

            if event.invitation_perm == INVITATION_PERM_PARTICIPANTS:
                event_participants = EventParticipant.objects.filter(event=event).select_related('user')
                potential_inviters.extend([p.user for p in event_participants])
            elif event.invitation_perm == INVITATION_PERM_ADMINS:
                admin_participants = EventParticipant.objects.filter(
                    event=event,
                    is_admin=True
                ).select_related('user')
                potential_inviters.extend([p.user for p in admin_participants])

            if not potential_inviters:
                continue

            num_invitations = random.randint(min_count, max_count)

            existing_invitation_user_ids: Set[int] = set(
                EventInvitation.objects.filter(event=event).values_list('invited_user_id', flat=True)
            )

            potential_invitees = [
                u for u in users
                if u.id not in existing_participant_ids
                and u.id not in existing_invitation_user_ids
            ]

            if not potential_invitees:
                continue

            invitees = random_sample(potential_invitees, num_invitations)

            for invitee in invitees:
                inviter = random_choice(potential_inviters)
                status = random_choice(statuses)

                try:
                    EventInvitation.objects.create(
                        event=event,
                        invited_user=invitee,
                        invited_by=inviter,
                        status=status,
                    )
                    created_count += 1
                except Exception:
                    continue

        self.stdout.write(f'  Created {created_count} invitations across events')
        return created_count
