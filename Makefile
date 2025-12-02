dev:
	uv run python manage.py runserver 0.0.0.0:8000

prod:
	uv run python manage.py runserver 0.0.0.0:8000

dev-docker:
	docker compose up

stop-docker:
	docker compose down

seed-docker:
	docker compose exec web uv run python manage.py seed_data