# API Documentation

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
All protected endpoints require JWT authentication via the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## Endpoints Overview

### Authentication
- `POST /api/auth/signup/` - Register new user
- `POST /api/auth/login/` - Login user
- `GET /api/auth/me/` - Get current user info (protected)

### Events
- `GET /api/events/` - List all upcoming events
- `POST /api/events/` - Create new event (protected)
- `GET /api/events/{id}/` - Get event details
- `PUT /api/events/{id}/` - Update event (protected, organizer only)
- `DELETE /api/events/{id}/` - Delete event (protected, organizer only)
- `POST /api/events/{id}/register/` - Register for event (protected)
- `POST /api/events/{id}/cancel_registration/` - Cancel registration (protected)
- `GET /api/events/my_organized/` - Get user's organized events (protected)
- `GET /api/events/my_registered/` - Get user's registered events (protected)

---

## Detailed Endpoints

### 1. User Registration

**Endpoint:** `POST /api/auth/signup/`

**Description:** Register a new user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Validations:**
- `email`: Must be valid email format and unique
- `name`: Required
- `password`: Minimum 6 characters

**Success Response (201):**
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

**Error Response (400):**
```json
{
  "email": ["This field must be unique."],
  "password": ["This field must be at least 6 characters."]
}
```

---

### 2. User Login

**Endpoint:** `POST /api/auth/login/`

**Description:** Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (200):**
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

**Error Response (400):**
```json
{
  "non_field_errors": ["Неверные учетные данные"]
}
```

---

### 3. Get Current User

**Endpoint:** `GET /api/auth/me/`

**Description:** Get information about the authenticated user.

**Authentication:** Required

**Success Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-10-11T10:00:00Z"
}
```

**Error Response (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 4. List Events

**Endpoint:** `GET /api/events/`

**Description:** Get list of all upcoming events.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Success Response (200):**
```json
{
  "count": 50,
  "next": "http://127.0.0.1:8000/api/events/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Django Meetup",
      "description": "Обсуждение лучших практик Django",
      "date": "2025-10-20T18:00:00Z",
      "organizer": {
        "id": 1,
        "email": "organizer@example.com",
        "name": "John Doe",
        "created_at": "2025-10-11T10:00:00Z"
      },
      "participants_count": 15,
      "is_registered": false
    }
  ]
}
```

---

### 5. Create Event

**Endpoint:** `POST /api/events/`

**Description:** Create a new event. User becomes the organizer automatically.

**Authentication:** Required

**Request Body:**
```json
{
  "title": "Python Workshop",
  "description": "Hands-on Python workshop for beginners",
  "date": "2025-11-01T14:00:00Z"
}
```

**Validations:**
- `title`: Required, max 255 characters
- `description`: Required
- `date`: Must be in the future

**Success Response (201):**
```json
{
  "id": 2,
  "title": "Python Workshop",
  "description": "Hands-on Python workshop for beginners",
  "date": "2025-11-01T14:00:00Z",
  "organizer": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-10-11T10:00:00Z"
  },
  "participants": [],
  "participants_count": 0,
  "is_registered": false,
  "created_at": "2025-10-11T11:00:00Z",
  "updated_at": "2025-10-11T11:00:00Z"
}
```

**Error Response (400):**
```json
{
  "date": ["Дата мероприятия должна быть в будущем"]
}
```

---

### 6. Get Event Details

**Endpoint:** `GET /api/events/{id}/`

**Description:** Get detailed information about a specific event, including participants list.

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Django Meetup",
  "description": "Обсуждение лучших практик Django",
  "date": "2025-10-20T18:00:00Z",
  "organizer": {
    "id": 1,
    "email": "organizer@example.com",
    "name": "John Doe",
    "created_at": "2025-10-11T10:00:00Z"
  },
  "participants": [
    {
      "id": 2,
      "email": "participant@example.com",
      "name": "Jane Smith",
      "created_at": "2025-10-11T09:00:00Z"
    }
  ],
  "participants_count": 1,
  "is_registered": false,
  "created_at": "2025-10-10T10:00:00Z",
  "updated_at": "2025-10-11T10:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Not found."
}
```

---

### 7. Register for Event

**Endpoint:** `POST /api/events/{id}/register/`

**Description:** Register current user as a participant for the event.

**Authentication:** Required

**Business Rules:**
- User cannot register for their own event
- User cannot register twice for the same event

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Django Meetup",
  "description": "Обсуждение лучших практик Django",
  "date": "2025-10-20T18:00:00Z",
  "organizer": { ... },
  "participants": [ ... ],
  "participants_count": 16,
  "is_registered": true,
  "created_at": "2025-10-10T10:00:00Z",
  "updated_at": "2025-10-11T12:00:00Z"
}
```

**Error Response (400):**
```json
{
  "error": "Вы не можете зарегистрироваться на свое мероприятие"
}
```

OR

```json
{
  "error": "Вы уже зарегистрированы на это мероприятие"
}
```

---

### 8. Cancel Registration

**Endpoint:** `POST /api/events/{id}/cancel_registration/`

**Description:** Cancel user's registration for the event.

**Authentication:** Required

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Django Meetup",
  "description": "Обсуждение лучших практик Django",
  "date": "2025-10-20T18:00:00Z",
  "organizer": { ... },
  "participants": [ ... ],
  "participants_count": 15,
  "is_registered": false,
  "created_at": "2025-10-10T10:00:00Z",
  "updated_at": "2025-10-11T12:30:00Z"
}
```

**Error Response (400):**
```json
{
  "error": "Вы не зарегистрированы на это мероприятие"
}
```

---

### 9. My Organized Events

**Endpoint:** `GET /api/events/my_organized/`

**Description:** Get list of events organized by current user.

**Authentication:** Required

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "Django Meetup",
    "description": "Обсуждение лучших практик Django",
    "date": "2025-10-20T18:00:00Z",
    "organizer": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2025-10-11T10:00:00Z"
    },
    "participants_count": 15,
    "is_registered": false
  }
]
```

---

### 10. My Registered Events

**Endpoint:** `GET /api/events/my_registered/`

**Description:** Get list of events where current user is registered as participant.

**Authentication:** Required

**Success Response (200):**
```json
[
  {
    "id": 2,
    "title": "Python Workshop",
    "description": "Hands-on Python workshop",
    "date": "2025-11-01T14:00:00Z",
    "organizer": {
      "id": 3,
      "email": "another@example.com",
      "name": "Alice Brown",
      "created_at": "2025-10-11T08:00:00Z"
    },
    "participants_count": 20,
    "is_registered": true
  }
]
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required or invalid token |
| 403 | Forbidden - No permission to access resource |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

---

## Rate Limiting

Currently no rate limiting is implemented. Consider adding for production.

---

## CORS

CORS is configured to allow all origins in development. Update for production to specific domains.

---

## Testing with cURL

### Register User
```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"test123"}'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Create Event
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"title":"Test Event","description":"Test description","date":"2025-12-01T10:00:00Z"}'
```

### Register for Event
```bash
curl -X POST http://127.0.0.1:8000/api/events/1/register/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
