"""
Shared utilities for database seeding commands.

Provides common functionality used across all seeder commands including
random data generation, date utilities, and progress reporting.
"""

from typing import List, TypeVar, Any
from datetime import timedelta
import random

from django.utils import timezone
from faker import Faker


# Initialize Faker instance (shared across all seeders)
fake: Faker = Faker()

T = TypeVar('T')


def random_choice(items: List[T]) -> T:
    """
    Select a random item from a list.

    Args:
        items: List of items to choose from.

    Returns:
        A random item from the list.
    """
    return random.choice(items)


def random_sample(items: List[T], count: int) -> List[T]:
    """
    Select random items from a list without replacement.

    Args:
        items: List of items to choose from.
        count: Number of items to select.

    Returns:
        List of randomly selected items.
    """
    return random.sample(items, min(count, len(items)))


def weighted_choice(items: List[T], weights: List[int]) -> T:
    """
    Select a random item from a list with weights.

    Args:
        items: List of items to choose from.
        weights: List of weights corresponding to each item.

    Returns:
        A randomly selected item based on weights.
    """
    return random.choices(items, weights=weights, k=1)[0]


def random_bool(probability: float = 0.5) -> bool:
    """
    Generate a random boolean with given probability of True.

    Args:
        probability: Probability of returning True (0.0 to 1.0).

    Returns:
        Random boolean value.
    """
    return random.random() < probability


def random_date_in_range(days_from: int, days_to: int, hour_start: int = 9, hour_end: int = 20) -> Any:
    """
    Generate a random datetime within a range of days from now.

    Args:
        days_from: Start of range (negative for past, positive for future).
        days_to: End of range (negative for past, positive for future).
        hour_start: Earliest hour of day (0-23).
        hour_end: Latest hour of day (0-23).

    Returns:
        Random timezone-aware datetime.
    """
    days_offset = random.randint(days_from, days_to)
    hours_offset = random.randint(hour_start, hour_end)
    return timezone.now() + timedelta(days=days_offset, hours=hours_offset)


def future_date(days_ahead_min: int = 1, days_ahead_max: int = 90) -> Any:
    """
    Generate a random future datetime.

    Args:
        days_ahead_min: Minimum days in the future.
        days_ahead_max: Maximum days in the future.

    Returns:
        Random future datetime.
    """
    return random_date_in_range(days_ahead_min, days_ahead_max)


def past_date(days_ago_min: int = 1, days_ago_max: int = 365) -> Any:
    """
    Generate a random past datetime.

    Args:
        days_ago_min: Minimum days in the past.
        days_ago_max: Maximum days in the past.

    Returns:
        Random past datetime.
    """
    return random_date_in_range(-days_ago_max, -days_ago_min)


def print_success(message: str) -> None:
    """
    Print a success message (green).

    Args:
        message: Message to print.
    """
    from django.core.management.base import BaseCommand
    cmd = BaseCommand()
    cmd.stdout.write(cmd.style.SUCCESS(message))


def print_warning(message: str) -> None:
    """
    Print a warning message (yellow).

    Args:
        message: Message to print.
    """
    from django.core.management.base import BaseCommand
    cmd = BaseCommand()
    cmd.stdout.write(cmd.style.WARNING(message))


def print_error(message: str) -> None:
    """
    Print an error message (red).

    Args:
        message: Message to print.
    """
    from django.core.management.base import BaseCommand
    cmd = BaseCommand()
    cmd.stdout.write(cmd.style.ERROR(message))


def print_info(message: str) -> None:
    """
    Print an info message (normal).

    Args:
        message: Message to print.
    """
    from django.core.management.base import BaseCommand
    cmd = BaseCommand()
    cmd.stdout.write(message)
