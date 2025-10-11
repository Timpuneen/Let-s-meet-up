# ER-диаграмма базы данных Let's Meet Up

## Визуальная схема

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USERS (Пользователи)                          │
├─────────────────────────────────────────────────────────────────────────┤
│ • id (BIGSERIAL) PK                                                     │
│ • email (VARCHAR 255) UNIQUE NOT NULL  ← логин                         │
│ • name (VARCHAR 255) NOT NULL                                           │
│ • password (VARCHAR 128) NOT NULL      ← хешированный                  │
│ • is_active (BOOLEAN) DEFAULT TRUE                                      │
│ • is_staff (BOOLEAN) DEFAULT FALSE                                      │
│ • is_superuser (BOOLEAN) DEFAULT FALSE                                  │
│ • last_login (TIMESTAMP) NULL                                           │
│ • created_at (TIMESTAMP) NOT NULL                                       │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │ organizes
                        │ (1 : N)
                        │ ON DELETE CASCADE
                        │
                        ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          EVENTS (Мероприятия)                           │
├─────────────────────────────────────────────────────────────────────────┤
│ • id (BIGSERIAL) PK                                                     │
│ • title (VARCHAR 255) NOT NULL                                          │
│ • description (TEXT) NOT NULL                                           │
│ • date (TIMESTAMP) NOT NULL            ← дата проведения               │
│ • organizer_id (BIGINT) FK NOT NULL    ─┐                              │
│ • created_at (TIMESTAMP) NOT NULL       │                              │
│ • updated_at (TIMESTAMP) NOT NULL       │                              │
└─────────────────────┬───────────────────┘                              │
                      │                                                    │
                      │ has participants                                  │
                      │ (N : M)                                           │
                      │                                                    │
                      ↓                                                    │
┌─────────────────────────────────────────────────────────────────────────┤
│                   EVENTS_PARTICIPANTS (Участники)                       │
│                        [Junction Table]                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ • id (BIGSERIAL) PK                                                     │
│ • event_id (BIGINT) FK NOT NULL        ─────────────────────────────────┘
│ • user_id (BIGINT) FK NOT NULL         ────────┐
│                                                 │
│ UNIQUE (event_id, user_id)                     │
│ ON DELETE CASCADE (оба FK)                     │
└─────────────────────────────────────────────────┘
                                                  │
                          participates in         │
                          (N : M)                 │
                          ON DELETE CASCADE       │
                                                  │
                                                  ↓
                                  ┌───────────────────────────┐
                                  │  users (тот же пользователь)│
                                  └───────────────────────────┘
```

## Описание связей

### 1️⃣ Users → Events (One-to-Many)
```
[ONE User] ─── organizes ──→ [MANY Events]
```
- Один пользователь может создать много мероприятий
- Каждое мероприятие имеет одного организатора
- FK: `events.organizer_id` → `users.id`
- При удалении пользователя удаляются все его мероприятия (CASCADE)

### 2️⃣ Events ↔ Users через Events_Participants (Many-to-Many)
```
[MANY Users] ←─── participates ───→ [MANY Events]
                       ↕
              [events_participants]
```
- Один пользователь может участвовать в многих мероприятиях
- Одно мероприятие может иметь много участников
- FK1: `events_participants.event_id` → `events.id`
- FK2: `events_participants.user_id` → `users.id`
- Уникальное ограничение: один пользователь = одна регистрация на мероприятие
- При удалении пользователя или мероприятия удаляются связи (CASCADE)

## Индексы для производительности

### 👤 Таблица USERS
```
┌─ PRIMARY KEY: id
├─ UNIQUE INDEX: email (для быстрого поиска при входе)
└─ INDEX: is_active (для фильтрации активных пользователей)
```

### 📅 Таблица EVENTS
```
┌─ PRIMARY KEY: id
├─ INDEX: date (для поиска предстоящих мероприятий)
├─ INDEX: organizer_id (для поиска мероприятий пользователя)
└─ INDEX: created_at (для сортировки по дате создания)
```

### 🔗 Таблица EVENTS_PARTICIPANTS
```
┌─ PRIMARY KEY: id
├─ UNIQUE INDEX: (event_id, user_id) (предотвращает дубликаты)
├─ INDEX: event_id (для быстрого поиска участников мероприятия)
└─ INDEX: user_id (для быстрого поиска мероприятий пользователя)
```

## Примеры типичных запросов

### 📋 Список всех предстоящих мероприятий
```sql
SELECT * FROM events 
WHERE date >= NOW() 
ORDER BY date ASC;
```

### 👨‍💼 Мероприятия, организованные пользователем #1
```sql
SELECT * FROM events 
WHERE organizer_id = 1 
ORDER BY date DESC;
```

### ✋ Мероприятия, на которые зарегистрирован пользователь #1
```sql
SELECT e.* 
FROM events e
INNER JOIN events_participants ep ON e.id = ep.event_id
WHERE ep.user_id = 1
ORDER BY e.date ASC;
```

### 👥 Все участники мероприятия #1
```sql
SELECT u.id, u.name, u.email 
FROM users u
INNER JOIN events_participants ep ON u.id = ep.user_id
WHERE ep.event_id = 1;
```

### 📊 Мероприятия с количеством участников
```sql
SELECT 
    e.id,
    e.title,
    e.date,
    u.name as organizer_name,
    COUNT(ep.user_id) as participants_count
FROM events e
LEFT JOIN users u ON e.organizer_id = u.id
LEFT JOIN events_participants ep ON e.id = ep.event_id
WHERE e.date >= NOW()
GROUP BY e.id, u.name
ORDER BY e.date ASC;
```

## Правила целостности данных

### ✅ Constraints
1. **UNIQUE** (users.email) - один email = один пользователь
2. **UNIQUE** (event_id, user_id) - один пользователь = одна регистрация
3. **NOT NULL** для критических полей
4. **CHECK** (date >= NOW()) - в Django валидации
5. **CASCADE DELETE** для всех FK

### 🔒 Бизнес-правила
1. ❌ Пользователь НЕ может зарегистрироваться на свое мероприятие
2. ❌ Нельзя зарегистрироваться дважды на одно мероприятие
3. ✅ Дата мероприятия должна быть в будущем
4. ✅ Email должен быть уникальным
5. ✅ Пароль хешируется автоматически

## Статистика схемы

| Параметр | Значение |
|----------|----------|
| Основных таблиц | 3 |
| Связей (FK) | 3 |
| Many-to-Many | 1 |
| Индексов | 11 |
| UNIQUE constraints | 2 |
| CASCADE rules | 3 |

## Нормализация: 3NF ✅

База данных соответствует **Третьей Нормальной Форме (3NF)**:
- ✅ **1NF**: Атомарные значения, нет повторяющихся групп
- ✅ **2NF**: Все атрибуты зависят от полного первичного ключа
- ✅ **3NF**: Нет транзитивных зависимостей

## Потенциальные улучшения (для будущего)

### 🚀 Оптимизации
- [ ] Добавить полнотекстовый поиск по events.title и events.description
- [ ] Партиционирование events по дате (для старых мероприятий)
- [ ] Materialized view для популярных мероприятий

### 📈 Расширения
- [ ] Таблица `categories` (категории мероприятий)
- [ ] Таблица `comments` (комментарии к мероприятиям)
- [ ] Таблица `notifications` (уведомления пользователей)
- [ ] Таблица `ratings` (рейтинги мероприятий)

### 🔄 Дополнительные поля
- [ ] `events_participants.status` (pending, confirmed, cancelled)
- [ ] `events_participants.registered_at` (дата регистрации)
- [ ] `events.max_participants` (лимит участников)
- [ ] `events.location` (место проведения)
- [ ] `users.avatar_url` (аватар пользователя)
