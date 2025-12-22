"""
Seeder command for categories app.

Seeds the database with event categories.
"""

from typing import Any, List

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.categories.models import Category


class Command(BaseSeederCommand):
    """
    Seed event categories.

    Creates predefined event categories for classification.
    This is a foundation seeder with no dependencies.
    """

    help = 'Seed event categories'

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Categories'

    def seed_data(self, **options: Any) -> int:
        """
        Seed categories.

        Args:
            **options: Command options.

        Returns:
            Number of categories created.
        """
        categories = self._create_categories()
        return len(categories)

    def clear_data(self) -> None:
        """Clear all categories."""
        Category.objects.all().delete()

    def _create_categories(self) -> List[Category]:
        """
        Create event categories.

        Returns:
            List of created Category instances.
        """
        category_names: List[str] = [
            'Sports & Fitness',
            'Technology',
            'Business & Professional',
            'Arts & Culture',
            'Food & Drink',
            'Music',
            'Health & Wellness',
            'Education',
            'Outdoor & Adventure',
            'Gaming',
            'Social Activities',
            'Photography',
            'Travel',
            'Language & Culture',
            'Volunteering',
            'Books & Reading',
            'Movies & Film',
            'Dance',
            'Crafts',
            'Pets & Animals',
        ]

        categories: List[Category] = []
        for name in category_names:
            slug = name.lower().replace(' & ', '-').replace(' ', '-')
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'slug': slug}
            )
            categories.append(category)

        self.stdout.write(f'  Created {len(categories)} categories')
        return categories
