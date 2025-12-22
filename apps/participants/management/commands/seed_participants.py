"""
Seeder command for participants app.

Seeds the database with event participants.
"""

from typing import Any, List
import random

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.core.utils.seeding import random_sample, random_bool
from apps.participants.models import EventParticipant
from apps.events.models import Event
from apps.users.models import User


DEFAULT_MIN_PARTICIPANTS: int = 3
DEFAULT_MAX_PARTICIPANTS: int = 12
ADMIN_PROBABILITY: float = 0.15


class Command(BaseSeederCommand):
    """
    Seed event participant data.

    Creates participants for events.
    Depends on: Events, Users.
    """

    help = 'Seed event participants'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--min',
            type=int,
            default=DEFAULT_MIN_PARTICIPANTS,
            help=f'Minimum participants per event (default: {DEFAULT_MIN_PARTICIPANTS})',
        )
        parser.add_argument(
            '--max',
            type=int,
            default=DEFAULT_MAX_PARTICIPANTS,
            help=f'Maximum participants per event (default: {DEFAULT_MAX_PARTICIPANTS})',
        )

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Participants'

    def seed_data(self, **options: Any) -> int:
        """
        Seed participants.

        Args:
            **options: Command options including 'min' and 'max'.

        Returns:
            Number of participants created.
        """
        self.check_dependencies({
            'Event': Event,
            'User': User,
        })

        min_participants: int = options.get('min', DEFAULT_MIN_PARTICIPANTS)
        max_participants: int = options.get('max', DEFAULT_MAX_PARTICIPANTS)

        participants_created = self._create_participants(min_participants, max_participants)
        return participants_created

    def clear_data(self) -> None:
        """Clear all participants."""
        EventParticipant.objects.all().delete()

    def _create_participants(self, min_count: int, max_count: int) -> int:
        """
        Create participants for all events.

        Args:
            min_count: Minimum participants per event.
            max_count: Maximum participants per event.

        Returns:
            Total number of participants created.
        """
        events: List[Event] = list(Event.objects.all())
        users: List[User] = list(User.objects.all())

        if not events or not users:
            self.stdout.write(self.style.ERROR('Missing required data'))
            return 0

        created_count: int = 0

        for event in events:
            num_participants = random.randint(min_count, max_count)

            if event.max_participants:
                num_participants = min(num_participants, event.max_participants - 1)

            potential_participants = [u for u in users if u != event.organizer]

            participants = random_sample(potential_participants, num_participants)

            for user in participants:
                if not EventParticipant.objects.filter(event=event, user=user).exists():
                    is_admin = random_bool(ADMIN_PROBABILITY)

                    EventParticipant.objects.create(
                        event=event,
                        user=user,
                        is_admin=is_admin,
                    )
                    created_count += 1

        self.stdout.write(f'  Created {created_count} participants across {len(events)} events')
        return created_count
