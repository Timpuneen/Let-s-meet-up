#!/bin/bash
set -e

cd /app/project

echo "Waiting for db"
until uv run python -c "import psycopg2; psycopg2.connect(dbname='${DB_NAME}', user='${DB_USER}', password='${DB_PASSWORD}', host='db', port='5432')" 2>/dev/null; do
  sleep 1
done

echo "Running migrations"
uv run python manage.py migrate --noinput

echo "Collecting static files"
uv run python manage.py collectstatic --noinput

echo "Starting server"
exec uv run "$@"

