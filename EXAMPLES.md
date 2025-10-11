# Примеры HTTP запросов

## 1. Регистрация пользователя

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ivan@example.com",
    "name": "Иван Иванов",
    "password": "password123"
  }'
```

### HTTPie
```bash
http POST http://127.0.0.1:8000/api/auth/signup/ \
  email=ivan@example.com \
  name="Иван Иванов" \
  password=password123
```

### PowerShell
```powershell
$body = @{
    email = "ivan@example.com"
    name = "Иван Иванов"
    password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/signup/" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

## 2. Вход пользователя

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ivan@example.com",
    "password": "password123"
  }'
```

### HTTPie
```bash
http POST http://127.0.0.1:8000/api/auth/login/ \
  email=ivan@example.com \
  password=password123
```

### PowerShell
```powershell
$body = @{
    email = "ivan@example.com"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login/" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

# Сохраняем токен для последующих запросов
$token = $response.tokens.access
Write-Host "Access Token: $token"
```

---

## 3. Получить информацию о текущем пользователе

### cURL
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### HTTPie
```bash
http GET http://127.0.0.1:8000/api/auth/me/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### PowerShell
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/me/" `
  -Method GET `
  -Headers $headers
```

---

## 4. Получить список мероприятий

### cURL
```bash
curl -X GET http://127.0.0.1:8000/api/events/
```

### HTTPie
```bash
http GET http://127.0.0.1:8000/api/events/
```

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/" -Method GET
```

---

## 5. Создать мероприятие

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Python Митап",
    "description": "Обсуждение новых фич Python 3.12",
    "date": "2025-11-15T18:00:00Z"
  }'
```

### HTTPie
```bash
http POST http://127.0.0.1:8000/api/events/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  title="Python Митап" \
  description="Обсуждение новых фич Python 3.12" \
  date="2025-11-15T18:00:00Z"
```

### PowerShell
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

$body = @{
    title = "Python Митап"
    description = "Обсуждение новых фич Python 3.12"
    date = "2025-11-15T18:00:00Z"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/" `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

---

## 6. Получить детали мероприятия

### cURL
```bash
curl -X GET http://127.0.0.1:8000/api/events/1/
```

### HTTPie
```bash
http GET http://127.0.0.1:8000/api/events/1/
```

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/1/" -Method GET
```

---

## 7. Зарегистрироваться на мероприятие

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/events/1/register/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### HTTPie
```bash
http POST http://127.0.0.1:8000/api/events/1/register/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### PowerShell
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/1/register/" `
  -Method POST `
  -Headers $headers
```

---

## 8. Отменить регистрацию на мероприятие

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/events/1/cancel_registration/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### HTTPie
```bash
http POST http://127.0.0.1:8000/api/events/1/cancel_registration/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### PowerShell
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/1/cancel_registration/" `
  -Method POST `
  -Headers $headers
```

---

## 9. Получить мои организованные мероприятия

### cURL
```bash
curl -X GET http://127.0.0.1:8000/api/events/my_organized/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### HTTPie
```bash
http GET http://127.0.0.1:8000/api/events/my_organized/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### PowerShell
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/my_organized/" `
  -Method GET `
  -Headers $headers
```

---

## 10. Получить мероприятия, на которые я зарегистрирован

### cURL
```bash
curl -X GET http://127.0.0.1:8000/api/events/my_registered/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### HTTPie
```bash
http GET http://127.0.0.1:8000/api/events/my_registered/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### PowerShell
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/my_registered/" `
  -Method GET `
  -Headers $headers
```

---

## Полный сценарий использования (PowerShell)

```powershell
# 1. Регистрация пользователя
$signupBody = @{
    email = "test@example.com"
    name = "Тестовый Пользователь"
    password = "test123456"
} | ConvertTo-Json

$signupResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/signup/" `
  -Method POST `
  -ContentType "application/json" `
  -Body $signupBody

$token = $signupResponse.tokens.access
Write-Host "✓ Пользователь зарегистрирован. Token: $token"

# 2. Создание мероприятия
$headers = @{ Authorization = "Bearer $token" }

$eventBody = @{
    title = "Тестовое мероприятие"
    description = "Описание тестового мероприятия"
    date = "2025-12-01T15:00:00Z"
} | ConvertTo-Json

$eventResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/" `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $eventBody

$eventId = $eventResponse.id
Write-Host "✓ Мероприятие создано с ID: $eventId"

# 3. Получение списка мероприятий
$events = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/" -Method GET
Write-Host "✓ Найдено мероприятий: $($events.count)"

# 4. Получение деталей мероприятия
$eventDetails = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/$eventId/" -Method GET
Write-Host "✓ Детали мероприятия получены: $($eventDetails.title)"

# 5. Проверка моих организованных мероприятий
$myOrganized = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/my_organized/" `
  -Method GET `
  -Headers $headers
Write-Host "✓ Организованных мероприятий: $($myOrganized.Length)"

Write-Host "`n=== Тестирование завершено успешно ==="
```

---

## Примечания

1. **Замените `YOUR_ACCESS_TOKEN`** на реальный токен, полученный при входе
2. **Даты** должны быть в формате ISO 8601 (например: `2025-11-15T18:00:00Z`)
3. Токен **действителен 1 час**, после чего нужно использовать `refresh` токен для получения нового
4. Для **production** не забудьте изменить URL с `127.0.0.1:8000` на ваш домен
