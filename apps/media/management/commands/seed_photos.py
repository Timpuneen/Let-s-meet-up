"""
Seeder command for media app (event photos).

Seeds the database with event photos.
"""

from typing import Any, List, Callable
import random

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.core.utils.seeding import fake, random_choice, random_bool
from apps.media.models import EventPhoto
from apps.events.models import Event
from apps.participants.models import EventParticipant
from apps.users.models import User


DEFAULT_PHOTO_COUNT: int = 100
DEFAULT_MIN_PHOTOS_PER_EVENT: int = 1
DEFAULT_MAX_PHOTOS_PER_EVENT: int = 5


class Command(BaseSeederCommand):
    """
    Seed event photo data.

    Creates photos for events with URLs from placeholder services.
    Depends on: Events, Users, Participants.
    """

    help = 'Seed event photos'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--count',
            type=int,
            default=DEFAULT_PHOTO_COUNT,
            help=f'Target number of photos to create (default: {DEFAULT_PHOTO_COUNT})',
        )
        parser.add_argument(
            '--min-per-event',
            type=int,
            default=DEFAULT_MIN_PHOTOS_PER_EVENT,
            help=f'Minimum photos per event (default: {DEFAULT_MIN_PHOTOS_PER_EVENT})',
        )
        parser.add_argument(
            '--max-per-event',
            type=int,
            default=DEFAULT_MAX_PHOTOS_PER_EVENT,
            help=f'Maximum photos per event (default: {DEFAULT_MAX_PHOTOS_PER_EVENT})',
        )

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Media (Photos)'

    def seed_data(self, **options: Any) -> int:
        """
        Seed photos.

        Args:
            **options: Command options.

        Returns:
            Number of photos created.
        """
        self.check_dependencies({
            'Event': Event,
            'User': User,
            'EventParticipant': EventParticipant,
        })

        target_count: int = options.get('count', DEFAULT_PHOTO_COUNT)
        min_per_event: int = options.get('min_per_event', DEFAULT_MIN_PHOTOS_PER_EVENT)
        max_per_event: int = options.get('max_per_event', DEFAULT_MAX_PHOTOS_PER_EVENT)

        photos_created = self._create_photos(target_count, min_per_event, max_per_event)
        return photos_created

    def clear_data(self) -> None:
        """Clear all photos."""
        EventPhoto.objects.all().delete()

    def _create_photos(self, target_count: int, min_per_event: int, max_per_event: int) -> int:
        """
        Create event photos.

        Args:
            target_count: Target total number of photos.
            min_per_event: Minimum photos per event.
            max_per_event: Maximum photos per event.

        Returns:
            Number of photos created.
        """
        events: List[Event] = list(Event.objects.all())

        if not events:
            self.stdout.write(self.style.ERROR('No events found'))
            return 0

        photo_sources: List[Callable[[], str]] = [
            lambda: f"https://picsum.photos/seed/{random.randint(1, 10000)}/800/600",
            lambda: f"https://source.unsplash.com/800x600/?{random_choice(['party', 'conference', 'meeting', 'sports', 'concert', 'food', 'nature', 'people', 'fitness', 'travel'])}",
            lambda: f"https://via.placeholder.com/800x600/{random_choice(['FF6B6B', '4ECDC4', '45B7D1', 'FFA07A', '98D8C8', 'F7DC6F', 'BB8FCE'])}/FFFFFF?text=Event+Photo",
        ]

        created_count: int = 0
        events_processed: int = 0

        for event in events:
            if created_count >= target_count:
                break

            participants = EventParticipant.objects.filter(event=event).select_related('user')
            potential_uploaders = [p.user for p in participants] + [event.organizer]

            if not potential_uploaders:
                continue

            num_photos = random.randint(min_per_event, max_per_event)

            for i in range(num_photos):
                if created_count >= target_count:
                    break

                uploader = random_choice(potential_uploaders)
                source_generator = random_choice(photo_sources)
                photo_url = source_generator()

                EventPhoto.objects.create(
                    event=event,
                    uploaded_by=uploader,
                    url=photo_url,
                    caption=fake.sentence() if random_bool(0.5) else None,
                    is_cover=(i == 0)
                )
                created_count += 1

            events_processed += 1

        self.stdout.write(
            f'  Created {created_count} photos across {events_processed} events'
        )
        return created_count
