.PHONY: run install dev lint lint-fix format docker-up docker-down docker-logs docker-build

install:
	uv sync

dev:
	uv sync --extra dev

run:
	uv run uvicorn src.app:app --reload --host 127.0.0.1 --port 8000

# Docker Compose commands
docker-build:
	docker compose build

docker-up:
	docker compose up -d --build

docker-db:
	docker compose up -d postgres

docker-down:
	docker compose down

docker-clean:
	docker compose down -v
	-docker volume rm shared-notes_postgres_data

lint:
	uv run ruff check ./
	uv run isort --check-only ./
	uv run ruff format --check ./

lint-fix:
	uv run ruff check --fix ./
	uv run isort ./
	uv run ruff format ./

format:
	uv run ruff format ./

test:
	uv run pytest

test-cov:
	uv run pytest --cov=src --cov-report=term-missing

# Database commands
db-migrate:
	uv run alembic revision --autogenerate -m "$(message)"

db-upgrade:
	uv run alembic upgrade head

db-downgrade:
	uv run alembic downgrade -1

db-history:
	uv run alembic history

db-current:
	uv run alembic current
