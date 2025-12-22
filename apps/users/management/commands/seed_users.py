"""
Seeder command for users app.

Seeds the database with users including a superuser admin account.
"""

from typing import Any, List

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.core.utils.seeding import fake, random_choice
from apps.users.models import User, INVITATION_PRIVACY_EVERYONE, INVITATION_PRIVACY_FRIENDS, INVITATION_PRIVACY_NONE


DEFAULT_USER_COUNT: int = 60
DEFAULT_PASSWORD: str = 'password123'
ADMIN_EMAIL: str = 'admin@letsmeetup.com'
ADMIN_PASSWORD: str = 'admin123'


class Command(BaseSeederCommand):
    """
    Seed user data.

    Creates regular users and optionally a superuser admin account.
    This is a foundation seeder with no dependencies.
    """

    help = 'Seed users and admin account'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--count',
            type=int,
            default=DEFAULT_USER_COUNT,
            help=f'Number of regular users to create (default: {DEFAULT_USER_COUNT})',
        )
        parser.add_argument(
            '--create-admin',
            action='store_true',
            default=True,
            help='Create admin superuser account (default: True)',
        )

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Users'

    def seed_data(self, **options: Any) -> int:
        """
        Seed users.

        Args:
            **options: Command options including 'count' and 'create_admin'.

        Returns:
            Number of users created.
        """
        count: int = options.get('count', DEFAULT_USER_COUNT)
        create_admin: bool = options.get('create_admin', True)

        users: List[User] = []

        if create_admin:
            admin = self._create_admin()
            if admin:
                users.append(admin)

        regular_users = self._create_users(count)
        users.extend(regular_users)

        return len(users)

    def clear_data(self) -> None:
        """Clear all non-superuser users."""
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('  Preserved superuser accounts')

    def _create_admin(self) -> User | None:
        """
        Create or get admin superuser.

        Returns:
            Admin User instance or None if already exists.
        """
        if User.objects.filter(email=ADMIN_EMAIL).exists():
            self.stdout.write(f'  Admin user already exists: {ADMIN_EMAIL}')
            return User.objects.get(email=ADMIN_EMAIL)

        admin = User.objects.create_superuser(
            email=ADMIN_EMAIL,
            name='Admin User',
            password=ADMIN_PASSWORD,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'  Created admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}'
            )
        )
        return admin

    def _create_users(self, count: int) -> List[User]:
        """
        Create regular users.

        Args:
            count: Number of users to create.

        Returns:
            List of created User instances.
        """
        privacy_choices: List[str] = [
            INVITATION_PRIVACY_EVERYONE,
            INVITATION_PRIVACY_FRIENDS,
            INVITATION_PRIVACY_NONE
        ]

        users: List[User] = []

        for i in range(count):
            name: str = fake.name()
            email: str = fake.email()

            if User.objects.filter(email=email).exists():
                email = f"{fake.user_name()}_{i}@example.com"

            user = User.objects.create_user(
                email=email,
                name=name,
                password=DEFAULT_PASSWORD,
                invitation_privacy=random_choice(privacy_choices),
                is_active=random_choice([True, True, True, False])
            )
            users.append(user)

        self.stdout.write(f'  Created {len(users)} regular users')
        return users
