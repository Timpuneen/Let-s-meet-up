# Let's Meet Up - Meetup Platform Backend MVP

Backend MVP для платформы по организации мероприятий, митапов и воркшопов.

## 📋 Описание проекта

Это RESTful API бэкенд для платформы создания и посещения мероприятий. Пользователи могут регистрироваться, создавать мероприятия и участвовать в мероприятиях других пользователей.

## 🛠 Технологический стек

- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.15.2
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Environment**: django-environ

## 🏗 Архитектура проекта

Проект имеет модульную структуру:

```
project/
├── users/          # Модуль управления пользователями
│   ├── models.py   # Кастомная модель User
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── events/         # Модуль управления мероприятиями
│   ├── models.py   # Модель Event
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── project/        # Настройки проекта
    ├── settings.py
    └── urls.py
```

## 📊 Модели данных

### User (Пользователь)
- `id`: Уникальный идентификатор (автоматически)
- `email`: Email (уникальный, используется для входа)
- `name`: Имя пользователя
- `password`: Хешированный пароль
- `is_active`: Активен ли пользователь
- `created_at`: Дата создания

### Event (Мероприятие)
- `id`: Уникальный идентификатор
- `title`: Название мероприятия
- `description`: Описание
- `date`: Дата и время проведения
- `organizer`: Организатор (ForeignKey → User)
- `participants`: Участники (ManyToMany → User)
- `created_at`, `updated_at`: Даты создания и обновления

## 🔌 API Endpoints

### Аутентификация (`/api/auth/`)

#### Регистрация
```http
POST /api/auth/signup/
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-10-11T10:00:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

#### Вход
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Получить текущего пользователя
```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

### Мероприятия (`/api/events/`)

#### Получить список предстоящих мероприятий
```http
GET /api/events/
```

#### Получить детали мероприятия
```http
GET /api/events/{id}/
```

#### Создать мероприятие
```http
POST /api/events/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Django Meetup",
  "description": "Обсуждение лучших практик Django",
  "date": "2025-10-20T18:00:00Z"
}
```

#### Зарегистрироваться на мероприятие
```http
POST /api/events/{id}/register/
Authorization: Bearer <access_token>
```

#### Отменить регистрацию
```http
POST /api/events/{id}/cancel_registration/
Authorization: Bearer <access_token>
```

#### Мои организованные мероприятия
```http
GET /api/events/my_organized/
Authorization: Bearer <access_token>
```

#### Мои зарегистрированные мероприятия
```http
GET /api/events/my_registered/
Authorization: Bearer <access_token>
```

## 🚀 Установка и запуск

### Предварительные требования

- Python 3.11+
- PostgreSQL 12+
- pip

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/yourusername/Let-s-meet-up.git
cd Let-s-meet-up
```

### Шаг 2: Создание виртуального окружения

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

```bash
pip install -r reqs.txt
```

### Шаг 4: Настройка базы данных PostgreSQL

Создайте базу данных в PostgreSQL:

```sql
CREATE DATABASE meetup_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE meetup_db TO postgres;
```

### Шаг 5: Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте значения:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
# Django настройки
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# База данных PostgreSQL
DB_NAME=meetup_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# CORS настройки
CORS_ALLOW_ALL_ORIGINS=True
```

### Шаг 6: Применение миграций

```bash
cd project
python manage.py makemigrations
python manage.py migrate
```

### Шаг 7: Создание суперпользователя (опционально)

```bash
python manage.py createsuperuser
```

### Шаг 8: Запуск сервера разработки

```bash
python manage.py runserver
```

Сервер будет доступен по адресу: `http://127.0.0.1:8000/`

## 🔐 Аутентификация

API использует JWT (JSON Web Token) для аутентификации.

### Получение токена

После регистрации или входа вы получите два токена:
- `access`: Используется для авторизации запросов (срок действия: 1 час)
- `refresh`: Используется для обновления access токена (срок действия: 7 дней)

### Использование токена

Добавьте токен в заголовок `Authorization`:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 📝 Примеры использования

### 1. Регистрация пользователя

```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "name": "John Doe",
    "password": "password123"
  }'
```

### 2. Создание мероприятия

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Python Workshop",
    "description": "Hands-on Python workshop",
    "date": "2025-11-01T14:00:00Z"
  }'
```

### 3. Регистрация на мероприятие

```bash
curl -X POST http://127.0.0.1:8000/api/events/1/register/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🧪 Тестирование

### Через Django Admin

Доступ к админ-панели: `http://127.0.0.1:8000/admin/`

### Через API клиенты

- **Postman**: Импортируйте коллекцию API endpoints
- **cURL**: Примеры выше
- **HTTPie**: `http POST http://127.0.0.1:8000/api/auth/login/ email=user@example.com password=pass123`

## 📚 Дополнительная информация

### Бизнес-логика

- ✅ Пользователь **не может** зарегистрироваться на свое собственное мероприятие
- ✅ Пароли хранятся в **хешированном виде** (Django pbkdf2_sha256)
- ✅ JWT токены передаются в заголовке `Authorization: Bearer <token>`
- ✅ Регистрация реализована через связь **ManyToMany** в модели Event
- ✅ Только **предстоящие мероприятия** показываются в списке по умолчанию

### Безопасность

- Пароли хешируются через Django's `set_password()`
- JWT токены с ограниченным сроком действия
- CORS настроен (по умолчанию разрешены все источники для разработки)
- Чувствительные данные в `.env` файле

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для деталей.

## 👤 Автор

Ваше имя - [@yourusername](https://github.com/yourusername)

---

**Примечание**: Это MVP версия. Для production необходимо:
- Изменить `SECRET_KEY` и `DEBUG=False`
- Настроить CORS для конкретных доменов
- Добавить rate limiting
- Настроить логирование
- Добавить юнит-тесты
- Настроить CI/CD
