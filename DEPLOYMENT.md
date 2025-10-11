# Deployment Guide

## Развертывание на Production

### Предварительная подготовка

1. **Обновите зависимости для production**:
   ```bash
   pip install gunicorn whitenoise
   ```

2. **Обновите `reqs.txt`**:
   ```bash
   pip freeze > reqs.txt
   ```

### Настройки для Production

#### 1. Обновите `.env`

```env
# Django настройки
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# База данных
DB_NAME=meetup_production
DB_USER=prod_user
DB_PASSWORD=very_secure_password
DB_HOST=db.yourdomain.com
DB_PORT=5432

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 2. Обновите `settings.py`

Добавьте в конец файла:

```python
# Production settings
if not DEBUG:
    # Security
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Static files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### Развертывание на Heroku

#### 1. Создайте `Procfile`

```
web: gunicorn project.wsgi --log-file -
release: python project/manage.py migrate
```

#### 2. Создайте `runtime.txt`

```
python-3.11.9
```

#### 3. Инициализация Git

```bash
git init
git add .
git commit -m "Initial commit"
```

#### 4. Создайте приложение Heroku

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
```

#### 5. Настройте переменные окружения

```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
heroku config:set CORS_ALLOW_ALL_ORIGINS=False
heroku config:set CORS_ALLOWED_ORIGINS="https://your-frontend-domain.com"
```

#### 6. Деплой

```bash
git push heroku main
heroku run python project/manage.py createsuperuser
```

### Развертывание на VPS (Ubuntu)

#### 1. Установите зависимости на сервере

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib
```

#### 2. Настройте PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE meetup_production;
CREATE USER prod_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE meetup_production TO prod_user;
\q
```

#### 3. Клонируйте проект

```bash
cd /var/www
git clone https://github.com/yourusername/Let-s-meet-up.git
cd Let-s-meet-up
```

#### 4. Создайте виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r reqs.txt
pip install gunicorn
```

#### 5. Настройте `.env`

```bash
nano .env
# Заполните production значениями
```

#### 6. Соберите статику и примените миграции

```bash
cd project
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

#### 7. Настройте Gunicorn systemd service

Создайте `/etc/systemd/system/meetup.service`:

```ini
[Unit]
Description=Meetup Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/Let-s-meet-up/project
Environment="PATH=/var/www/Let-s-meet-up/venv/bin"
ExecStart=/var/www/Let-s-meet-up/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/Let-s-meet-up/meetup.sock \
    project.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start meetup
sudo systemctl enable meetup
```

#### 8. Настройте Nginx

Создайте `/etc/nginx/sites-available/meetup`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/Let-s-meet-up/project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/Let-s-meet-up/meetup.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/meetup /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. Настройте SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Развертывание с Docker

#### 1. Создайте `Dockerfile`

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY reqs.txt /app/
RUN pip install --no-cache-dir -r reqs.txt

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "project", "project.wsgi:application"]
```

#### 2. Создайте `docker-compose.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: meetup_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 --chdir project project.wsgi:application
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

volumes:
  postgres_data:
```

#### 3. Запустите

```bash
docker-compose up -d
docker-compose exec web python project/manage.py migrate
docker-compose exec web python project/manage.py createsuperuser
```

### Мониторинг и Логирование

#### Настройте логирование в `settings.py`

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/meetup/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Backup базы данных

#### Создайте скрипт backup

```bash
#!/bin/bash
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/meetup"
pg_dump -U prod_user meetup_production > "$BACKUP_DIR/backup_$DATE.sql"
find $BACKUP_DIR -type f -mtime +7 -delete
```

Добавьте в cron:
```bash
0 2 * * * /path/to/backup.sh
```

### Checklist для Production

- [ ] `DEBUG=False`
- [ ] Изменен `SECRET_KEY`
- [ ] Настроен `ALLOWED_HOSTS`
- [ ] Настроен CORS для конкретных доменов
- [ ] SSL/TLS сертификат установлен
- [ ] Статические файлы собраны
- [ ] Миграции применены
- [ ] Создан суперпользователь
- [ ] Настроен firewall
- [ ] Настроено логирование
- [ ] Настроен backup базы данных
- [ ] Настроен мониторинг (Sentry, New Relic и т.д.)

### Рекомендации по безопасности

1. **Используйте сильные пароли** для БД и пользователей
2. **Регулярно обновляйте** зависимости
3. **Настройте rate limiting** для API endpoints
4. **Используйте HTTPS** везде
5. **Настройте firewall** (UFW на Ubuntu)
6. **Регулярно делайте backup**
7. **Мониторьте логи** на подозрительную активность
8. **Используйте environment variables** для чувствительных данных
