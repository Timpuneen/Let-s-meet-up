"""
Скрипт для создания тестовых данных
Запуск: python create_test_data.py
"""
import os
import django
from users.models import User
from events.models import Event
from django.utils import timezone
from datetime import timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()



print("🚀 Создание тестовых данных...")

# Очистка существующих данных (осторожно!)
print("\n⚠️  Очистка существующих данных...")
User.objects.all().delete()
Event.objects.all().delete()

# Создание пользователей
print("\n👥 Создание пользователей...")
users_data = [
    {
        'email': 'ivan@example.com',
        'name': 'Иван Иванов',
        'password': 'password123'
    },
    {
        'email': 'maria@example.com',
        'name': 'Мария Петрова',
        'password': 'password123'
    },
    {
        'email': 'alex@example.com',
        'name': 'Алексей Сидоров',
        'password': 'password123'
    },
    {
        'email': 'elena@example.com',
        'name': 'Елена Смирнова',
        'password': 'password123'
    },
]

users = []
for user_data in users_data:
    user = User.objects.create_user(**user_data)
    users.append(user)
    print(f"   ✓ Создан пользователь: {user.name} ({user.email})")

# Создание мероприятий
print("\n📅 Создание мероприятий...")
events_data = [
    {
        'title': 'Python Meetup Moscow',
        'description': 'Обсуждение новых возможностей Python 3.12 и лучших практик разработки. Рассмотрим новые фичи, performance improvements и breaking changes.',
        'date': timezone.now() + timedelta(days=7, hours=2),
        'organizer': users[0]
    },
    {
        'title': 'Django Workshop',
        'description': 'Практический workshop по разработке REST API с Django. Изучим DRF, аутентификацию, оптимизацию запросов и deployment.',
        'date': timezone.now() + timedelta(days=14, hours=3),
        'organizer': users[0]
    },
    {
        'title': 'React + Django Integration',
        'description': 'Как интегрировать React фронтенд с Django бэкендом. CORS, JWT, state management и best practices.',
        'date': timezone.now() + timedelta(days=21, hours=4),
        'organizer': users[1]
    },
    {
        'title': 'PostgreSQL Performance Tuning',
        'description': 'Оптимизация производительности PostgreSQL для веб-приложений. Индексы, explain analyze, партиционирование.',
        'date': timezone.now() + timedelta(days=28, hours=5),
        'organizer': users[2]
    },
    {
        'title': 'Docker & DevOps',
        'description': 'Введение в контейнеризацию и CI/CD для Python проектов. Docker, docker-compose, GitHub Actions.',
        'date': timezone.now() + timedelta(days=35, hours=6),
        'organizer': users[3]
    },
    {
        'title': 'Git Advanced',
        'description': 'Продвинутые техники работы с Git. Rebase, cherry-pick, bisect, hooks и workflow стратегии.',
        'date': timezone.now() + timedelta(days=42, hours=7),
        'organizer': users[1]
    },
]

events = []
for event_data in events_data:
    event = Event.objects.create(**event_data)
    events.append(event)
    print(f"   ✓ Создано мероприятие: {event.title}")

# Регистрация участников на мероприятия
print("\n✍️  Регистрация участников...")

# Python Meetup - много участников
events[0].participants.add(users[1], users[2], users[3])
print(f"   ✓ {events[0].title}: 3 участника")

# Django Workshop
events[1].participants.add(users[1], users[3])
print(f"   ✓ {events[1].title}: 2 участника")

# React + Django
events[2].participants.add(users[0], users[3])
print(f"   ✓ {events[2].title}: 2 участника")

# PostgreSQL
events[3].participants.add(users[0], users[1])
print(f"   ✓ {events[3].title}: 2 участника")

# Docker & DevOps - популярное
events[4].participants.add(users[0], users[1], users[2])
print(f"   ✓ {events[4].title}: 3 участника")

# Git Advanced
events[5].participants.add(users[2])
print(f"   ✓ {events[5].title}: 1 участник")

# Статистика
print("\n📊 Статистика:")
print(f"   Пользователей: {User.objects.count()}")
print(f"   Мероприятий: {Event.objects.count()}")
total_registrations = sum(e.participants.count() for e in Event.objects.all())
print(f"   Всего регистраций: {total_registrations}")

print("\n🔑 Тестовые учетные данные:")
print("   " + "="*60)
for user in users:
    print(f"   Email: {user.email:25} | Password: password123")
print("   " + "="*60)

print("\n✅ Тестовые данные успешно созданы!")
print("\n💡 Подсказка:")
print("   1. Войдите под любым пользователем через POST /api/auth/login/")
print("   2. Используйте полученный токен в заголовке Authorization")
print("   3. Попробуйте создать мероприятие и зарегистрироваться на другие")
print("\n   Admin панель: http://127.0.0.1:8000/admin/")
