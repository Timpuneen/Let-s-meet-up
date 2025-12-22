"""
Abstract base class for seeder commands.

Provides common functionality and interface for all package-specific seeders.
"""

from typing import Any
from abc import ABC, abstractmethod

from django.core.management.base import BaseCommand
from django.db import transaction


class BaseSeederCommand(BaseCommand, ABC):
    """
    Abstract base class for database seeder commands.

    Provides common functionality including:
    - Standard --clear flag handling
    - Progress reporting
    - Transaction management
    - Consistent output formatting
    """

    help: str = 'Seed database with data'

    def add_arguments(self, parser: Any) -> None:
        """
        Add common arguments for all seeders.

        Args:
            parser: Argument parser.
        """
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data for this app before seeding',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Main entry point for the command.

        Args:
            *args: Variable length argument list.
            **options: Command options.
        """
        if options['clear']:
            self.stdout.write(self.style.WARNING(f'Clearing {self.get_app_name()} data...'))
            self.clear_data()
            self.stdout.write(self.style.SUCCESS(f'{self.get_app_name()} data cleared'))

        self.stdout.write(self.style.SUCCESS(f'Starting {self.get_app_name()} seeding...'))

        try:
            with transaction.atomic():
                count = self.seed_data(**options)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {self.get_app_name()} seeding completed: {count} objects created'
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during {self.get_app_name()} seeding: {str(e)}'))
            raise

    @abstractmethod
    def seed_data(self, **options: Any) -> int:
        """
        Seed the database with data for this app.

        Must be implemented by subclasses.

        Args:
            **options: Command options.

        Returns:
            Number of objects created.
        """
        pass

    @abstractmethod
    def clear_data(self) -> None:
        """
        Clear existing data for this app.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_app_name(self) -> str:
        """
        Get the name of the app being seeded.

        Must be implemented by subclasses.

        Returns:
            App name (e.g., 'Geography', 'Users').
        """
        pass

    def check_dependencies(self, dependencies: dict[str, Any]) -> None:
        """
        Check if required dependencies exist.

        Args:
            dependencies: Dict mapping model names to their counts.

        Raises:
            SystemExit: If dependencies are missing.
        """
        missing = []
        for name, model in dependencies.items():
            if model.objects.count() == 0:
                missing.append(name)

        if missing:
            self.stdout.write(
                self.style.ERROR(
                    f'Missing required dependencies: {", ".join(missing)}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Please run the required seeders first, or use "seed_all" command.'
                )
            )
            raise SystemExit(1)
