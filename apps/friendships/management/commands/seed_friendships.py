"""
Seeder command for friendships app.

Seeds the database with user friendships.
"""

from typing import Any, List

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.core.utils.seeding import random_choice, weighted_choice
from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED, FRIENDSHIP_STATUS_PENDING
from apps.users.models import User


DEFAULT_FRIENDSHIP_COUNT: int = 150


class Command(BaseSeederCommand):
    """
    Seed friendship data.

    Creates friendships between users with varied statuses.
    Depends on: Users.
    """

    help = 'Seed friendships'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--count',
            type=int,
            default=DEFAULT_FRIENDSHIP_COUNT,
            help=f'Number of friendships to create (default: {DEFAULT_FRIENDSHIP_COUNT})',
        )

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Friendships'

    def seed_data(self, **options: Any) -> int:
        """
        Seed friendships.

        Args:
            **options: Command options including 'count'.

        Returns:
            Number of friendships created.
        """
        # Check dependencies
        self.check_dependencies({'User': User})

        count: int = options.get('count', DEFAULT_FRIENDSHIP_COUNT)
        friendships_created = self._create_friendships(count)
        return friendships_created

    def clear_data(self) -> None:
        """Clear all friendships."""
        Friendship.objects.all().delete()

    def _create_friendships(self, count: int) -> int:
        """
        Create friendships between users.

        Args:
            count: Target number of friendships to create.

        Returns:
            Number of friendships actually created.
        """
        users: List[User] = list(User.objects.all())

        if len(users) < 2:
            self.stdout.write(self.style.ERROR('Need at least 2 users to create friendships'))
            return 0

        # 70% accepted, 30% pending
        statuses: List[str] = [FRIENDSHIP_STATUS_ACCEPTED] * 7 + [FRIENDSHIP_STATUS_PENDING] * 3

        created_count: int = 0
        attempts: int = 0
        max_attempts: int = count * 3  # Avoid infinite loops

        while created_count < count and attempts < max_attempts:
            attempts += 1

            sender = random_choice(users)
            receiver = random_choice(users)

            # Skip if same user
            if sender == receiver:
                continue

            # Skip if friendship already exists (in either direction)
            if Friendship.objects.filter(sender=sender, receiver=receiver).exists():
                continue
            if Friendship.objects.filter(sender=receiver, receiver=sender).exists():
                continue

            status = random_choice(statuses)

            Friendship.objects.create(
                sender=sender,
                receiver=receiver,
                status=status
            )
            created_count += 1

        self.stdout.write(f'  Created {created_count} friendships ({attempts} attempts)')
        return created_count
