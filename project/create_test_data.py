"""
Script for generating test data for the project.

Usage:
    python create_test_data.py

This script:
1. Initializes the Django environment.
2. Deletes all existing User and Event objects (including soft-deleted).
3. Creates a set of test users and events.
4. Registers participants for each event.
5. Displays summary statistics and test credentials.
"""
from users.models import User
from events.models import Event
import os
import django
from django.utils import timezone
from datetime import timedelta

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()




def main():
    """Main function to create test data."""
    print("Creating test data...")

    # Clear existing data (including soft-deleted records)
    print("\nClearing existing data...")
    print("   Deleting all events (including soft-deleted)...")
    event_count = Event.all_objects.count()
    for event in Event.all_objects.all():
        event.hard_delete()
    print(f"   Deleted {event_count} events")
    
    print("   Deleting all users (including soft-deleted)...")
    user_count = User.all_objects.count()
    for user in User.all_objects.all():
        user.hard_delete()
    print(f"   Deleted {user_count} users")

    # Create users
    print("\nCreating users...")
    users_data = [
        {'email': 'ivan@example.com', 'name': 'Ivan Ivanov', 'password': 'password123'},
        {'email': 'maria@example.com', 'name': 'Maria Petrova', 'password': 'password123'},
        {'email': 'alex@example.com', 'name': 'Alexey Sidorov', 'password': 'password123'},
        {'email': 'elena@example.com', 'name': 'Elena Smirnova', 'password': 'password123'},
        {'email': 'madina@example.com', 'name': 'Madina Kadyrova', 'password': '1234Qwerty!'},
        {'email': 'sultan@example.com', 'name': 'Sultan Kadyrov', 'password': '1234Qwerty!'},
        {'email': 'azamat@example.com', 'name': 'Azamat Kadyrov', 'password': '1234Qwerty!'},
        {'email': 'diana@example.com', 'name': 'Diana Kadyrova', 'password': '1234Qwerty!'},
        {'email': 'azamat@example.com', 'name': 'Azamat Kadyrov', 'password': '1234Qwerty!'},
        {'email': 'arslan@example.com', 'name': 'Arslan Kenesov', 'password': '1234Qwerty!'},
        {'email': 'kairat@example.com', 'name': 'Kairat Kenesov', 'password': '1234Qwerty!'},
        {'email': 'maxim@example.com', 'name': 'Maxim Kenesov', 'password': '1234Qwerty!'},
        {'email': 'vlad@example.com', 'name': 'Vlad Kozhuhov', 'password': '1234Qwerty!'},
        {'email': 'vladimir@example.com', 'name': 'Vladimir Zhenski', 'password': '1234Qwerty!'},
        {'email': 'bbbb@example.com', 'name': 'Boris Borisov', 'password': '1234Qwerty!'},
        {'email': 'nier@example.com', 'name': 'Nepal Aslanov', 'password': '1234Qwerty!'},
        {'email': 'timupher@example.com', 'name': 'Timupher Kenesov', 'password': '1234Qwerty!'},
        {'email': 'amiradil@example.com', 'name': 'Amir Adilov', 'password': '1234Qwerty!'},
        {'email': 'googleman@example.com', 'name': 'Grigory Popov', 'password': '1234Qwerty!'},
        {'email': 'niceguy@example.com', 'name': 'Vladimir Kuznetsov', 'password': '1234Qwerty!'}
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
        {
            'title': 'AI Workshop',
            'description': 'Workshop on using AI for data analysis and visualization.',
            'date': timezone.now() + timedelta(days=49, hours=8),
            'organizer': users[1],
        },
        {
            'title': 'Cybersecurity Basics',
            'description': 'Basics of cybersecurity: threat modeling, risk assessment, and mitigation strategies.',
            'date': timezone.now() + timedelta(days=56, hours=9),
            'organizer': users[4],
        },
        {
            'title': 'Blockchain Technology',
            'description': 'Introduction to blockchain technology and its applications in finance and supply chain.',
            'date': timezone.now() + timedelta(days=63, hours=10),
            'organizer': users[5],
        },
        {
            'title': 'Data Science',
            'description': 'Introduction to data science: data cleaning, visualization, and machine learning.',
            'date': timezone.now() + timedelta(days=70, hours=11),
            'organizer': users[6],
        },
        {
            'title': 'Web Development',
            'description': 'Introduction to web development: HTML, CSS, JavaScript, and frameworks.',
            'date': timezone.now() + timedelta(days=77, hours=12),
            'organizer': users[7],
        },
        {
            'title': 'Data Engineering',
            'description': 'Introduction to data engineering: data pipelines, ETL, and data warehousing.',
            'date': timezone.now() + timedelta(days=84, hours=13),
            'organizer': users[8],
        },
        {
            'title': 'Data Analysis',
            'description': 'Introduction to data analysis: data cleaning, visualization, and machine learning.',
            'date': timezone.now() + timedelta(days=91, hours=14),
            'organizer': users[9],
        },
        {
            'title': 'Cybersecurity Workshop',
            'description': 'Workshop on cybersecurity: threat modeling, risk assessment, and mitigation strategies.',
            'date': timezone.now() + timedelta(days=98, hours=15),
            'organizer': users[10],
        },
        {
            'title': 'Machine Learning Workshop',
            'description': 'Workshop on machine learning: data cleaning, visualization, and machine learning.',
            'date': timezone.now() + timedelta(days=105, hours=16),
            'organizer': users[11],
        },
        {
            'title': 'Data Science Workshop',
            'description': 'Workshop on data science: data cleaning, visualization, and machine learning.',
            'date': timezone.now() + timedelta(days=112, hours=17),
            'organizer': users[12],
        },
        {
            'title': 'Data Visualization Workshop',
            'description': 'Workshop on data visualization: data cleaning, visualization, and machine learning.',
            'date': timezone.now() + timedelta(days=119, hours=18),
            'organizer': users[13],
        },
        {
            'title': 'Data Engineering Workshop',
            'description': 'Workshop on data engineering: data pipelines, ETL, and data warehousing.',
            'date': timezone.now() + timedelta(days=126, hours=19),
            'organizer': users[14],
        },
        {
            'title': 'Data Analysis Workshop',
            'description': 'Workshop on data analysis: data cleaning, visualization, and machine learning.',
            'date': timezone.now() + timedelta(days=133, hours=20),
            'organizer': users[15],
        },
        {
            'title': 'Data Science Workshop',
            'description': 'Workshop on data science: data cleaning, visualization, and machine learning.',
            'date': timezone.now() + timedelta(days=140, hours=21),
            'organizer': users[16],
        },
        {
            'title': 'Advanced Go meetup',
            'description': 'Advanced Go meetup: best practices, performance optimization, and concurrency.',
            'date': timezone.now() + timedelta(days=147, hours=22),
            'organizer': users[17],
        },
        {
            'title': 'Advanced Python meetup',
            'description': 'Advanced Python meetup: best practices, performance optimization, and concurrency.',
            'date': timezone.now() + timedelta(days=154, hours=23),
        },
        {
            'title': 'Advanced Java meetup',
            'description': 'Advanced Java meetup: best practices, performance optimization, and concurrency.',
            'date': timezone.now() + timedelta(days=161, hours=24),
            'organizer': users[18],
        },
        {
            'title': 'Advanced C++ meetup',
            'description': 'Advanced C++ meetup: best practices, performance optimization, and concurrency.',
            'date': timezone.now() + timedelta(days=168, hours=25),
            'organizer': users[19],
        },
        {
            'title': 'Advanced C# meetup',
            'description': 'Advanced C# meetup: best practices, performance optimization, and concurrency.',
            'date': timezone.now() + timedelta(days=175, hours=26),
            'organizer': users[20],
        },
        {
            'title': 'Advanced Ruby meetup',
            'description': 'Advanced Ruby meetup: best practices, performance optimization, and concurrency.',
            'date': timezone.now() + timedelta(days=182, hours=27),
            'organizer': users[21],
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
    print(f"   Active users: {User.objects.count()}")
    print(f"   Active events: {Event.objects.count()}")
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