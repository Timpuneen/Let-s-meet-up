"""
Script for creating test data
Usage: python create_test_data.py
"""
import os
import django
from users.models import User
from events.models import Event
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()



print("🚀 Creating test data...")

# Clear existing data (be careful!)
print("\n⚠️  Clearing existing data...")
User.objects.all().delete()
Event.objects.all().delete()

# Create users
print("\n👥 Creating users...")
users_data = [
    {
        'email': 'ivan@example.com',
        'name': 'Ivan Ivanov',
        'password': 'password123'
    },
    {
        'email': 'maria@example.com',
        'name': 'Maria Petrova',
        'password': 'password123'
    },
    {
        'email': 'alex@example.com',
        'name': 'Alex Sidorov',
        'password': 'password123'
    },
    {
        'email': 'elena@example.com',
        'name': 'Elena Smirnova',
        'password': 'password123'
    },
]

users = []
for user_data in users_data:
    user = User.objects.create_user(**user_data)
    users.append(user)
    print(f"   ✓ Created user: {user.name} ({user.email})")

# Create events
print("\n📅 Creating events...")
events_data = [
    {
        'title': 'Python Meetup Moscow',
        'description': 'Discussion of new Python 3.12 features and development best practices. We will review new features, performance improvements and breaking changes.',
        'date': timezone.now() + timedelta(days=7, hours=2),
        'organizer': users[0]
    },
    {
        'title': 'Django Workshop',
        'description': 'Practical workshop on developing REST API with Django. We will study DRF, authentication, query optimization and deployment.',
        'date': timezone.now() + timedelta(days=14, hours=3),
        'organizer': users[0]
    },
    {
        'title': 'React + Django Integration',
        'description': 'How to integrate React frontend with Django backend. CORS, JWT, state management and best practices.',
        'date': timezone.now() + timedelta(days=21, hours=4),
        'organizer': users[1]
    },
    {
        'title': 'PostgreSQL Performance Tuning',
        'description': 'Performance optimization of PostgreSQL for web applications. Indexes, explain analyze, partitioning.',
        'date': timezone.now() + timedelta(days=28, hours=5),
        'organizer': users[2]
    },
    {
        'title': 'Docker & DevOps',
        'description': 'Introduction to containerization and CI/CD for Python projects. Docker, docker-compose, GitHub Actions.',
        'date': timezone.now() + timedelta(days=35, hours=6),
        'organizer': users[3]
    },
    {
        'title': 'Git Advanced',
        'description': 'Advanced Git techniques. Rebase, cherry-pick, bisect, hooks and workflow strategies.',
        'date': timezone.now() + timedelta(days=42, hours=7),
        'organizer': users[1]
    },
]

events = []
for event_data in events_data:
    event = Event.objects.create(**event_data)
    events.append(event)
    print(f"   ✓ Created event: {event.title}")

# Register participants for events
print("\n✍️  Registering participants...")

# Python Meetup - many participants
events[0].participants.add(users[1], users[2], users[3])
print(f"   ✓ {events[0].title}: 3 participants")

# Django Workshop
events[1].participants.add(users[1], users[3])
print(f"   ✓ {events[1].title}: 2 participants")

# React + Django
events[2].participants.add(users[0], users[3])
print(f"   ✓ {events[2].title}: 2 participants")

# PostgreSQL
events[3].participants.add(users[0], users[1])
print(f"   ✓ {events[3].title}: 2 participants")

# Docker & DevOps - popular
events[4].participants.add(users[0], users[1], users[2])
print(f"   ✓ {events[4].title}: 3 participants")

# Git Advanced
events[5].participants.add(users[2])
print(f"   ✓ {events[5].title}: 1 participant")

# Statistics
print("\n📊 Statistics:")
print(f"   Users: {User.objects.count()}")
print(f"   Events: {Event.objects.count()}")
total_registrations = sum(e.participants.count() for e in Event.objects.all())
print(f"   Total registrations: {total_registrations}")

print("\n🔑 Test credentials:")
print("   " + "="*60)
for user in users:
    print(f"   Email: {user.email:25} | Password: password123")
print("   " + "="*60)

print("\n✅ Test data created successfully!")
print("\n💡 Hint:")
print("   1. Login with any user via POST /api/auth/login/")
print("   2. Use the received token in Authorization header")
print("   3. Try to create an event and register for others")
print("\n   Admin panel: http://127.0.0.1:8000/admin/")
