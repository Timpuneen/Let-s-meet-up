"""
Script for generating test data for the project.

Usage:
    python create_test_data.py

This script:
1. Initializes the Django environment.
2. Deletes all existing User and Event objects.
3. Creates a set of test users and events.
4. Registers participants for each event.
5. Displays summary statistics and test credentials.
"""

import os
import django
from django.utils import timezone
from datetime import timedelta

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from users.models import User
from events.models import Event


def main():
    """Main function to create test data."""
    print("Creating test data...")

    # Clear existing data
    print("\nClearing existing data...")
    User.objects.all().delete()
    Event.objects.all().delete()

    # Create users
    print("\nCreating users...")
    users_data = [
        {'email': 'ivan@example.com', 'name': 'Ivan Ivanov', 'password': 'password123'},
        {'email': 'maria@example.com', 'name': 'Maria Petrova', 'password': 'password123'},
        {'email': 'alex@example.com', 'name': 'Alexey Sidorov', 'password': 'password123'},
        {'email': 'elena@example.com', 'name': 'Elena Smirnova', 'password': 'password123'},
    ]

    users = []
    for user_data in users_data:
        user = User.objects.create_user(**user_data)
        users.append(user)
        print(f"   Created user: {user.name} ({user.email})")

    # Create events
    print("\nCreating events...")
    events_data = [
        {
            'title': 'Python Meetup Moscow',
            'description': 'Discussion on new features of Python 3.12, best practices, and performance improvements.',
            'date': timezone.now() + timedelta(days=7, hours=2),
            'organizer': users[0],
        },
        {
            'title': 'Django Workshop',
            'description': 'Hands-on workshop on building REST APIs with Django and DRF.',
            'date': timezone.now() + timedelta(days=14, hours=3),
            'organizer': users[0],
        },
        {
            'title': 'React + Django Integration',
            'description': 'Integrating React frontend with Django backend: CORS, JWT, and best practices.',
            'date': timezone.now() + timedelta(days=21, hours=4),
            'organizer': users[1],
        },
        {
            'title': 'PostgreSQL Performance Tuning',
            'description': 'Performance optimization techniques for PostgreSQL: indexes, EXPLAIN ANALYZE, partitioning.',
            'date': timezone.now() + timedelta(days=28, hours=5),
            'organizer': users[2],
        },
        {
            'title': 'Docker & DevOps',
            'description': 'Introduction to containerization and CI/CD for Python projects using Docker and GitHub Actions.',
            'date': timezone.now() + timedelta(days=35, hours=6),
            'organizer': users[3],
        },
        {
            'title': 'Git Advanced',
            'description': 'Advanced Git techniques: rebase, cherry-pick, bisect, hooks, and branching strategies.',
            'date': timezone.now() + timedelta(days=42, hours=7),
            'organizer': users[1],
        },
    ]

    events = []
    for event_data in events_data:
        event = Event.objects.create(**event_data)
        events.append(event)
        print(f"   Created event: {event.title}")

    # Register participants
    print("\nRegistering participants...")

    events[0].participants.add(users[1], users[2], users[3])
    events[1].participants.add(users[1], users[3])
    events[2].participants.add(users[0], users[3])
    events[3].participants.add(users[0], users[1])
    events[4].participants.add(users[0], users[1], users[2])
    events[5].participants.add(users[2])

    # Display statistics
    print("\nSummary statistics:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Events: {Event.objects.count()}")
    total_registrations = sum(e.participants.count() for e in Event.objects.all())
    print(f"   Total registrations: {total_registrations}")

    # Display credentials
    print("\nTest credentials:")
    print("=" * 60)
    for user in users:
        print(f"   Email: {user.email:25} | Password: password123")
    print("=" * 60)

    print("\nTest data created successfully.")
    print("\nHints:")
    print("   1. Log in with any user via POST /api/auth/login/")
    print("   2. Use the received token in the Authorization header.")
    print("   3. Try creating an event or registering for others.")
    print("\n   Admin panel: http://127.0.0.1:8000/admin/")


if __name__ == "__main__":
    main()
