"""
Orchestrator command for seeding all database tables.

Executes all package-specific seeders in the correct dependency order.
"""

from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.geography.models import Country, City
from apps.users.models import User
from apps.categories.models import Category
from apps.events.models import Event
from apps.friendships.models import Friendship
from apps.participants.models import EventParticipant
from apps.invitations.models import EventInvitation
from apps.comments.models import EventComment
from apps.media.models import EventPhoto


class Command(BaseCommand):
    """
    Seed all database tables with realistic test data.

    Orchestrates all package-specific seeders in correct dependency order:
    1. Geography (Countries, Cities)
    2. Users
    3. Categories
    4. Events
    5. Friendships
    6. Participants
    7. Invitations
    8. Comments
    9. Photos
    """

    help = 'Seed all database tables with test data'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all data before seeding',
        )
        parser.add_argument(
            '--skip-geography',
            action='store_true',
            help='Skip geography seeding',
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip users seeding',
        )
        parser.add_argument(
            '--skip-categories',
            action='store_true',
            help='Skip categories seeding',
        )
        parser.add_argument(
            '--skip-events',
            action='store_true',
            help='Skip events seeding',
        )
        parser.add_argument(
            '--skip-friendships',
            action='store_true',
            help='Skip friendships seeding',
        )
        parser.add_argument(
            '--skip-participants',
            action='store_true',
            help='Skip participants seeding',
        )
        parser.add_argument(
            '--skip-invitations',
            action='store_true',
            help='Skip invitations seeding',
        )
        parser.add_argument(
            '--skip-comments',
            action='store_true',
            help='Skip comments seeding',
        )
        parser.add_argument(
            '--skip-photos',
            action='store_true',
            help='Skip photos seeding',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=60,
            help='Number of users to create (default: 60)',
        )
        parser.add_argument(
            '--events',
            type=int,
            default=40,
            help='Number of events to create (default: 40)',
        )
        parser.add_argument(
            '--friendships',
            type=int,
            default=150,
            help='Number of friendships to create (default: 150)',
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=200,
            help='Number of comments to create (default: 200)',
        )
        parser.add_argument(
            '--photos',
            type=int,
            default=100,
            help='Number of photos to create (default: 100)',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Execute all seeders in proper order.

        Args:
            *args: Variable length argument list.
            **options: Command options.
        """
        if options['clear']:
            self.clear_all_data()

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        self.stdout.write('=' * 70)

        try:
            with transaction.atomic():
                if not options['skip_geography']:
                    self.stdout.write('\n[1/9] Seeding Geography...')
                    call_command('seed_geography', verbosity=options.get('verbosity', 1))

                if not options['skip_users']:
                    self.stdout.write('\n[2/9] Seeding Users...')
                    call_command('seed_users', count=options['users'], verbosity=options.get('verbosity', 1))

                if not options['skip_categories']:
                    self.stdout.write('\n[3/9] Seeding Categories...')
                    call_command('seed_categories', verbosity=options.get('verbosity', 1))

                if not options['skip_events']:
                    self.stdout.write('\n[4/9] Seeding Events...')
                    call_command('seed_events', count=options['events'], verbosity=options.get('verbosity', 1))

                if not options['skip_friendships']:
                    self.stdout.write('\n[5/9] Seeding Friendships...')
                    call_command('seed_friendships', count=options['friendships'], verbosity=options.get('verbosity', 1))

                if not options['skip_participants']:
                    self.stdout.write('\n[6/9] Seeding Participants...')
                    call_command('seed_participants', verbosity=options.get('verbosity', 1))

                if not options['skip_invitations']:
                    self.stdout.write('\n[7/9] Seeding Invitations...')
                    call_command('seed_invitations', verbosity=options.get('verbosity', 1))

                if not options['skip_comments']:
                    self.stdout.write('\n[8/9] Seeding Comments...')
                    call_command('seed_comments', count=options['comments'], verbosity=options.get('verbosity', 1))

                if not options['skip_photos']:
                    self.stdout.write('\n[9/9] Seeding Photos...')
                    call_command('seed_photos', count=options['photos'], verbosity=options.get('verbosity', 1))

                self.stdout.write('\n' + '=' * 70)
                self.stdout.write(self.style.SUCCESS('✓ All seeding completed successfully!'))
                self.stdout.write('=' * 70)
                self.print_statistics()

        except Exception as e:
            self.stdout.write('\n' + '=' * 70)
            self.stdout.write(self.style.ERROR(f'✗ Error during seeding: {str(e)}'))
            self.stdout.write(self.style.WARNING('All changes have been rolled back.'))
            self.stdout.write('=' * 70)
            raise

    def clear_all_data(self) -> None:
        """Clear all seeded data from the database."""
        self.stdout.write(self.style.WARNING('Clearing all data...'))

        EventPhoto.objects.all().delete()
        EventComment.objects.all().delete()
        EventInvitation.objects.all().delete()
        EventParticipant.objects.all().delete()
        Friendship.objects.all().delete()
        Event.objects.all().delete()
        Category.objects.all().delete()
        City.objects.all().delete()
        Country.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('✓ All data cleared\n'))

    def print_statistics(self) -> None:
        """Print database statistics after seeding."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('Database Statistics:'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'  Countries:         {Country.objects.count()}')
        self.stdout.write(f'  Cities:            {City.objects.count()}')
        self.stdout.write(f'  Users:             {User.objects.count()}')
        self.stdout.write(f'  Categories:        {Category.objects.count()}')
        self.stdout.write(f'  Events:            {Event.objects.count()}')
        self.stdout.write(f'  Friendships:       {Friendship.objects.count()}')
        self.stdout.write(f'  Participants:      {EventParticipant.objects.count()}')
        self.stdout.write(f'  Invitations:       {EventInvitation.objects.count()}')
        self.stdout.write(f'    - Pending:       {EventInvitation.objects.filter(status="pending").count()}')
        self.stdout.write(f'    - Accepted:      {EventInvitation.objects.filter(status="accepted").count()}')
        self.stdout.write(f'    - Rejected:      {EventInvitation.objects.filter(status="rejected").count()}')
        self.stdout.write(f'  Comments:          {EventComment.objects.count()}')
        self.stdout.write(f'  Photos:            {EventPhoto.objects.count()}')
        self.stdout.write('=' * 70 + '\n')
