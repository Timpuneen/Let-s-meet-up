"""
Seeder command for events app.

Seeds the database with events.
"""

from typing import Any, List

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.core.utils.seeding import fake, random_choice, random_sample, future_date, past_date, weighted_choice
from apps.events.models import Event, EVENT_STATUS_PUBLISHED, EVENT_STATUS_COMPLETED, INVITATION_PERM_PARTICIPANTS, INVITATION_PERM_ADMINS, INVITATION_PERM_ORGANIZER
from apps.users.models import User
from apps.geography.models import Country, City
from apps.categories.models import Category


DEFAULT_EVENT_COUNT: int = 40


class Command(BaseSeederCommand):
    """
    Seed event data.

    Creates events with varied statuses, dates, and settings.
    Depends on: Users, Geography (Countries/Cities), Categories.
    """

    help = 'Seed events'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--count',
            type=int,
            default=DEFAULT_EVENT_COUNT,
            help=f'Number of events to create (default: {DEFAULT_EVENT_COUNT})',
        )

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Events'

    def seed_data(self, **options: Any) -> int:
        """
        Seed events.

        Args:
            **options: Command options including 'count'.

        Returns:
            Number of events created.
        """
        self.check_dependencies({
            'User': User,
            'Country': Country,
            'City': City,
            'Category': Category,
        })

        count: int = options.get('count', DEFAULT_EVENT_COUNT)
        events = self._create_events(count)
        return len(events)

    def clear_data(self) -> None:
        """Clear all events."""
        Event.objects.all().delete()

    def _create_events(self, count: int) -> List[Event]:
        """
        Create events with realistic data.

        Args:
            count: Number of events to create.

        Returns:
            List of created Event instances.
        """
        users: List[User] = list(User.objects.all())
        cities: List[City] = list(City.objects.all())
        categories: List[Category] = list(Category.objects.all())

        if not users or not cities or not categories:
            self.stdout.write(self.style.ERROR('Missing required data'))
            return []

        statuses: List[str] = [EVENT_STATUS_PUBLISHED] * 7 + [EVENT_STATUS_COMPLETED]
        invitation_perms: List[str] = [
            INVITATION_PERM_PARTICIPANTS
        ] * 6 + [INVITATION_PERM_ADMINS] * 3 + [INVITATION_PERM_ORGANIZER]

        event_titles: List[str] = [
            'Weekend Hiking Adventure', 'Tech Meetup: AI & Machine Learning',
            'Photography Walk in the City', 'Board Game Night',
            'Yoga in the Park', 'Startup Networking Event',
            'Language Exchange Meetup', 'Book Club Discussion',
            'Live Music Evening', 'Cooking Class: Italian Cuisine',
            'Marathon Training Group', 'Art Gallery Opening',
            'Coffee & Code Session', 'Volunteer Park Cleanup',
            'Dance Salsa Workshop', 'Film Screening & Discussion',
            'Rock Climbing Beginners', 'Business Pitch Practice',
            'Photography Portfolio Review', 'Gaming Tournament',
            'Wine Tasting Evening', 'Meditation & Mindfulness',
            'Street Food Tour', 'Tech Conference Afterparty',
            'Cycling Group Ride', 'Stand-up Comedy Night',
            'Pottery Workshop', 'Outdoor Movie Night',
            'Hackathon Weekend', 'Farmers Market Walk',
            'Karaoke Night', 'Chess Tournament',
            'Beach Volleyball', 'Craft Beer Tasting',
            'Sunrise Mountain Hike', 'Poetry Reading Event',
            'Escape Room Challenge', 'Picnic in the Park',
            'Photography Basics Workshop', 'Networking Brunch',
        ]

        events: List[Event] = []

        for i in range(count):
            organizer = random_choice(users)
            city = random_choice(cities)

            date_type = weighted_choice(
                ['future', 'recent_past', 'old_past'],
                [5, 3, 2]
            )

            if date_type == 'future':
                event_date = future_date(1, 90)
                status = EVENT_STATUS_PUBLISHED
            elif date_type == 'recent_past':
                event_date = past_date(1, 30)
                status = EVENT_STATUS_COMPLETED
            else:
                event_date = past_date(31, 365)
                status = EVENT_STATUS_COMPLETED

            title = random_choice(event_titles)

            event = Event.objects.create(
                title=f"{title} #{i + 1}",
                description=fake.paragraph(nb_sentences=5),
                address=fake.street_address(),
                date=event_date,
                status=status,
                invitation_perm=random_choice(invitation_perms),
                max_participants=random_choice([None, None, 10, 15, 20, 25, 30, 50]),
                organizer=organizer,
                country=city.country,
                city=city,
            )

            event_categories = random_sample(categories, weighted_choice([1, 2, 3], [2, 5, 3]))
            event.categories.set(event_categories)

            events.append(event)

        self.stdout.write(f'  Created {len(events)} events')
        return events
