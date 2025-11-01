.PHONY: run install dev lint lint-fix format

install:
	uv sync

dev:
	uv sync --extra dev

run:
	uv run uvicorn src.app:app --reload --host 127.0.0.1 --port 8000

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
