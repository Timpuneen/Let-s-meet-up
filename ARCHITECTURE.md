# Архитектурные решения и обоснования

## Обзор архитектуры

Проект построен на основе **Django REST Framework** с модульной архитектурой, разделяющей функциональность на отдельные приложения (apps).

## Принятые архитектурные решения

### 1. Модульная структура (Django Apps)

**Решение:** Проект разделен на два основных приложения:
- `users` - управление пользователями и аутентификация
- `events` - управление мероприятиями

**Обоснование:**
- ✅ **Separation of Concerns**: Каждый модуль отвечает за свою бизнес-логику
- ✅ **Масштабируемость**: Легко добавлять новые модули (например, `notifications`, `payments`)
- ✅ **Переиспользуемость**: Модули можно использовать в других проектах
- ✅ **Тестируемость**: Изолированные модули легче покрыть тестами

### 2. Кастомная модель пользователя

**Решение:** Использована кастомная модель `User` вместо стандартной Django `User`.

**Обоснование:**
- ✅ **Email как username**: Более современный подход, пользователи входят через email
- ✅ **Гибкость**: Легко добавлять дополнительные поля в будущем
- ✅ **Best Practice**: Django рекомендует использовать кастомную модель с начала проекта
- ✅ **Хеширование паролей**: Автоматически через `AbstractBaseUser` и `set_password()`

**Реализация:**
```python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # USERNAME_FIELD
    name = models.CharField(max_length=255)
    # password хешируется автоматически
```

### 3. JWT Authentication

**Решение:** Использована библиотека `djangorestframework-simplejwt` для JWT аутентификации.

**Обоснование:**
- ✅ **Stateless**: Сервер не хранит сессии, легко масштабируется
- ✅ **Mobile-friendly**: Токены легко использовать в мобильных приложениях
- ✅ **Microservices-ready**: JWT можно валидировать в разных сервисах
- ✅ **Security**: Короткий срок жизни access token (1 час), refresh token для обновления

**Конфигурация:**
- `access_token`: 1 час
- `refresh_token`: 7 дней
- Токен передается в заголовке: `Authorization: Bearer <token>`

### 4. Регистрация через ManyToMany

**Решение:** Регистрация на мероприятия реализована через `ManyToManyField` в модели `Event`.

**Обоснование:**
- ✅ **Простота**: Для MVP не нужна сложная логика регистрации
- ✅ **Производительность**: Django ORM эффективно работает с M2M связями
- ✅ **Гибкость**: В будущем можно добавить промежуточную модель `Registration` для хранения дополнительных данных (статус, дата регистрации и т.д.)

**Альтернатива (для будущего):**
```python
class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(...)  # pending, confirmed, cancelled
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'event')
```

### 5. ViewSets vs APIView

**Решение:** 
- `EventViewSet` - для CRUD операций с мероприятиями
- `APIView` - для аутентификации (signup, login)

**Обоснование:**
- ✅ **ViewSet для CRUD**: Автоматически генерирует стандартные endpoints (list, create, retrieve, update, delete)
- ✅ **APIView для кастомной логики**: Signup и login имеют специфическую бизнес-логику (генерация токенов)
- ✅ **Читаемость**: Код более понятен и структурирован

### 6. Сериализаторы

**Решение:** Использованы разные сериализаторы для разных операций:
- `EventListSerializer` - для списка (меньше данных)
- `EventSerializer` - для детального просмотра (все данные)
- `EventCreateSerializer` - для создания (только необходимые поля)

**Обоснование:**
- ✅ **Производительность**: Не загружаем лишние данные при списке
- ✅ **Безопасность**: Контроль над тем, какие данные можно изменять
- ✅ **Валидация**: Разная валидация для разных операций

### 7. Permissions

**Решение:** Использована комбинация permission classes:
- `IsAuthenticatedOrReadOnly` - для мероприятий (читать могут все, создавать только авторизованные)
- `IsAuthenticated` - для личных данных (me, my_organized, my_registered)
- `AllowAny` - для регистрации и входа

**Обоснование:**
- ✅ **Безопасность**: Контроль доступа на уровне view
- ✅ **Удобство**: Публичные мероприятия видны всем
- ✅ **Гибкость**: Легко изменить логику доступа

### 8. PostgreSQL

**Решение:** Использована PostgreSQL вместо SQLite или MySQL.

**Обоснование:**
- ✅ **Production-ready**: PostgreSQL - стандарт для Django проектов
- ✅ **Надежность**: ACID транзакции, referential integrity
- ✅ **Производительность**: Отличная работа с индексами и сложными запросами
- ✅ **Функциональность**: Полнотекстовый поиск, JSON поля, расширения

### 9. django-environ

**Решение:** Использована библиотека `django-environ` для работы с переменными окружения.

**Обоснование:**
- ✅ **12-Factor App**: Следование best practices
- ✅ **Безопасность**: Чувствительные данные не в коде
- ✅ **Гибкость**: Разные настройки для dev/staging/production
- ✅ **Удобство**: Простой синтаксис для работы с .env файлом

### 10. CORS Headers

**Решение:** Использована библиотека `django-cors-headers`.

**Обоснование:**
- ✅ **Frontend integration**: Необходимо для работы с SPA фронтендом
- ✅ **Безопасность**: Контроль над источниками запросов
- ✅ **Гибкость**: Легко настроить для production

## Бизнес-логика

### Ограничения при регистрации

**Решение:** Организатор не может зарегистрироваться на свое мероприятие.

**Обоснование:**
- ✅ **Логика**: Организатор и так участвует в своем мероприятии
- ✅ **Аналитика**: Четкое разделение организаторов и участников
- ✅ **UI/UX**: Упрощает интерфейс

**Реализация:**
```python
if event.organizer == user:
    return Response({'error': 'Вы не можете зарегистрироваться на свое мероприятие'})
```

### Только предстоящие мероприятия в списке

**Решение:** По умолчанию показываются только предстоящие мероприятия.

**Обоснование:**
- ✅ **Актуальность**: Пользователи интересуются предстоящими событиями
- ✅ **Производительность**: Меньше данных для обработки
- ✅ **Расширяемость**: Можно добавить фильтр для просмотра прошедших

**Реализация:**
```python
def get_queryset(self):
    if self.action == 'list':
        return Event.objects.filter(date__gte=timezone.now())
```

## Паттерны проектирования

### 1. Repository Pattern (через Django ORM)

Django ORM уже реализует Repository Pattern:
```python
Event.objects.filter(date__gte=timezone.now())
```

### 2. Serializer Pattern

Разделение представления данных от бизнес-логики:
```python
serializer = EventSerializer(event, context={'request': request})
```

### 3. Dependency Injection

Django DI через middleware и context processors:
```python
def get_is_registered(self, obj):
    request = self.context.get('request')
```

## Производительность

### Database Optimization

1. **select_related**: Для ForeignKey связей
   ```python
   Event.objects.select_related('organizer')
   ```

2. **prefetch_related**: Для ManyToMany связей
   ```python
   Event.objects.prefetch_related('participants')
   ```

3. **Индексы**: Автоматически для ForeignKey и unique полей

### Pagination

DRF автоматическая пагинация (20 элементов на страницу):
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

## Безопасность

### 1. Password Hashing
- Django pbkdf2_sha256 с 320,000 итераций
- Автоматически через `set_password()`

### 2. SQL Injection Protection
- Django ORM автоматически экранирует запросы

### 3. CSRF Protection
- Встроенная защита Django (отключена для API с JWT)

### 4. XSS Protection
- DRF автоматически экранирует JSON

### 5. Rate Limiting
- ⚠️ Не реализовано в MVP (рекомендуется для production)

## Масштабирование

### Horizontal Scaling

Проект готов к горизонтальному масштабированию:
- ✅ Stateless (JWT, нет сессий)
- ✅ Database pooling (через PostgreSQL)
- ✅ Static files (можно вынести в CDN)

### Возможные улучшения

1. **Caching**
   - Redis для кеширования списка мероприятий
   - Memcached для сессий (если понадобятся)

2. **Message Queue**
   - Celery для отправки уведомлений
   - RabbitMQ/Redis как брокер

3. **Search**
   - ElasticSearch для полнотекстового поиска
   - PostgreSQL Full Text Search как альтернатива

4. **CDN**
   - CloudFlare/AWS CloudFront для статики
   - Изображения мероприятий

## Тестирование

### Рекомендуемая структура тестов

```
tests/
├── test_models.py
├── test_serializers.py
├── test_views.py
├── test_permissions.py
└── test_integration.py
```

### Coverage Goals
- Unit tests: 80%+
- Integration tests: критические флоу
- E2E tests: основные пользовательские сценарии

## Выводы

Архитектура проекта следует принципам:
- **SOLID**: Особенно Single Responsibility и Dependency Inversion
- **DRY**: Код не дублируется
- **KISS**: Простые решения для MVP
- **YAGNI**: Не реализовано ничего лишнего

Проект готов к дальнейшему развитию и масштабированию.
