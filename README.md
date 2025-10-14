# Let`s meet up

## Установка и запуск

### Локальный запуск

```bash
uv sync
uv lock
uv run python project/manage.py runserver
```

### Docker

```bash
docker compose up
docker compose exec web uv run python manage.py createsuperuser
docker compose exec web uv run python manage.py create_test_data.py
```

## ER диаграмма

<div align="center">
  <img src="https://drive.google.com/uc?export=view&id=1WitrNtzZX4vp83umLgoIj-H_eKbNRk6X" alt="ER диаграмма базы данных" width="900"/>
  <p><em>Схема базы данных проекта</em></p>
</div>