# Тестовые данные для быстрой проверки

## Скрипт для создания тестовых данных

Создайте файл `project/create_test_data.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from users.models import User
from events.models import Event
from django.utils import timezone
from datetime import timedelta

print("🚀 Создание тестовых данных...")

# Очистка существующих данных
User.objects.all().delete()
Event.objects.all().delete()

# Создание пользователей
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
    print(f"✓ Создан пользователь: {user.name} ({user.email})")

# Создание мероприятий
events_data = [
    {
        'title': 'Python Meetup Moscow',
        'description': 'Обсуждение новых возможностей Python 3.12 и лучших практик разработки',
        'date': timezone.now() + timedelta(days=7),
        'organizer': users[0]
    },
    {
        'title': 'Django Workshop',
        'description': 'Практический workshop по разработке REST API с Django',
        'date': timezone.now() + timedelta(days=14),
        'organizer': users[0]
    },
    {
        'title': 'React + Django Integration',
        'description': 'Как интегрировать React фронтенд с Django бэкендом',
        'date': timezone.now() + timedelta(days=21),
        'organizer': users[1]
    },
    {
        'title': 'PostgreSQL Performance Tuning',
        'description': 'Оптимизация производительности PostgreSQL для веб-приложений',
        'date': timezone.now() + timedelta(days=28),
        'organizer': users[2]
    },
    {
        'title': 'Docker & DevOps',
        'description': 'Введение в контейнеризацию и CI/CD для Python проектов',
        'date': timezone.now() + timedelta(days=35),
        'organizer': users[3]
    },
]

events = []
for event_data in events_data:
    event = Event.objects.create(**event_data)
    events.append(event)
    print(f"✓ Создано мероприятие: {event.title}")

# Регистрация участников на мероприятия
# users[1] регистрируется на мероприятия users[0]
events[0].participants.add(users[1], users[2])
events[1].participants.add(users[1], users[3])

# users[0] регистрируется на мероприятия других
events[2].participants.add(users[0], users[3])
events[3].participants.add(users[0], users[1])

# users[2] регистрируется на разные мероприятия
events[4].participants.add(users[0], users[1], users[2])

print("\n✅ Тестовые данные успешно созданы!")
print("\n📊 Статистика:")
print(f"   Пользователей: {User.objects.count()}")
print(f"   Мероприятий: {Event.objects.count()}")
print(f"   Всего регистраций: {sum(e.participants.count() for e in Event.objects.all())}")

print("\n🔑 Тестовые учетные данные:")
for user in users:
    print(f"   Email: {user.email} | Password: password123")
```

## Запуск скрипта

```bash
cd project
python create_test_data.py
```

## Быстрая проверка API

### 1. Проверка списка мероприятий (без авторизации)

```bash
curl http://127.0.0.1:8000/api/events/
```

### 2. Вход с тестовым пользователем

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ivan@example.com",
    "password": "password123"
  }'
```

Сохраните полученный `access` токен.

### 3. Создание мероприятия

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Тестовое мероприятие",
    "description": "Описание тестового мероприятия",
    "date": "2025-12-15T18:00:00Z"
  }'
```

### 4. Регистрация на мероприятие

```bash
curl -X POST http://127.0.0.1:8000/api/events/1/register/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## PowerShell скрипт для полной проверки

Создайте файл `test_api.ps1`:

```powershell
$baseUrl = "http://127.0.0.1:8000"

Write-Host "🧪 Тестирование API..." -ForegroundColor Cyan

# 1. Проверка списка мероприятий
Write-Host "`n1. Получение списка мероприятий (публичный доступ)..." -ForegroundColor Yellow
$events = Invoke-RestMethod -Uri "$baseUrl/api/events/" -Method GET
Write-Host "   ✓ Найдено мероприятий: $($events.count)" -ForegroundColor Green

# 2. Вход
Write-Host "`n2. Вход пользователя ivan@example.com..." -ForegroundColor Yellow
$loginBody = @{
    email = "ivan@example.com"
    password = "password123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody

$token = $loginResponse.tokens.access
Write-Host "   ✓ Получен токен: $($token.Substring(0, 20))..." -ForegroundColor Green

# 3. Получение информации о текущем пользователе
Write-Host "`n3. Получение информации о текущем пользователе..." -ForegroundColor Yellow
$headers = @{ Authorization = "Bearer $token" }
$me = Invoke-RestMethod -Uri "$baseUrl/api/auth/me/" `
    -Method GET `
    -Headers $headers
Write-Host "   ✓ Пользователь: $($me.name) ($($me.email))" -ForegroundColor Green

# 4. Получение организованных мероприятий
Write-Host "`n4. Получение организованных мероприятий..." -ForegroundColor Yellow
$organized = Invoke-RestMethod -Uri "$baseUrl/api/events/my_organized/" `
    -Method GET `
    -Headers $headers
Write-Host "   ✓ Организовано мероприятий: $($organized.Length)" -ForegroundColor Green

# 5. Получение зарегистрированных мероприятий
Write-Host "`n5. Получение зарегистрированных мероприятий..." -ForegroundColor Yellow
$registered = Invoke-RestMethod -Uri "$baseUrl/api/events/my_registered/" `
    -Method GET `
    -Headers $headers
Write-Host "   ✓ Зарегистрировано на мероприятий: $($registered.Length)" -ForegroundColor Green

# 6. Создание нового мероприятия
Write-Host "`n6. Создание нового мероприятия..." -ForegroundColor Yellow
$newEventBody = @{
    title = "Автотест Мероприятие"
    description = "Создано автоматическим тестом"
    date = (Get-Date).AddDays(30).ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

$newEvent = Invoke-RestMethod -Uri "$baseUrl/api/events/" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $newEventBody
Write-Host "   ✓ Создано мероприятие ID: $($newEvent.id)" -ForegroundColor Green

# 7. Регистрация на мероприятие другого пользователя
Write-Host "`n7. Регистрация на мероприятие (ID=3)..." -ForegroundColor Yellow
try {
    $registration = Invoke-RestMethod -Uri "$baseUrl/api/events/3/register/" `
        -Method POST `
        -Headers $headers
    Write-Host "   ✓ Успешно зарегистрирован" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Уже зарегистрирован или это свое мероприятие" -ForegroundColor Yellow
}

# 8. Отмена регистрации
Write-Host "`n8. Отмена регистрации на мероприятие (ID=3)..." -ForegroundColor Yellow
try {
    $cancellation = Invoke-RestMethod -Uri "$baseUrl/api/events/3/cancel_registration/" `
        -Method POST `
        -Headers $headers
    Write-Host "   ✓ Регистрация отменена" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Не зарегистрирован на это мероприятие" -ForegroundColor Yellow
}

Write-Host "`n✅ Все тесты выполнены!" -ForegroundColor Green
```

Запуск:
```powershell
.\test_api.ps1
```

## Проверка через Django Admin

1. Создайте суперпользователя:
   ```bash
   python manage.py createsuperuser
   ```

2. Откройте админ-панель:
   ```
   http://127.0.0.1:8000/admin/
   ```

3. Проверьте:
   - Users (пользователи)
   - Events (мероприятия)
   - Связи participants

## Чеклист проверки

- [ ] GET /api/events/ - список мероприятий
- [ ] POST /api/auth/signup/ - регистрация
- [ ] POST /api/auth/login/ - вход
- [ ] GET /api/auth/me/ - текущий пользователь
- [ ] POST /api/events/ - создание мероприятия
- [ ] GET /api/events/{id}/ - детали мероприятия
- [ ] POST /api/events/{id}/register/ - регистрация на мероприятие
- [ ] POST /api/events/{id}/cancel_registration/ - отмена регистрации
- [ ] GET /api/events/my_organized/ - мои организованные
- [ ] GET /api/events/my_registered/ - мои зарегистрированные
- [ ] Проверка: нельзя зарегистрироваться на свое мероприятие
- [ ] Проверка: нельзя зарегистрироваться дважды
- [ ] Проверка: дата мероприятия должна быть в будущем

## Ожидаемые результаты

После создания тестовых данных:
- **4 пользователя**
- **5 мероприятий**
- **Несколько регистраций** участников

Все API endpoints должны работать корректно с валидацией и permission проверками.
