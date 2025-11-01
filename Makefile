.PHONY: run install dev lint lint-fix format

install:
	uv sync

dev:
	uv sync --extra dev

run:
	uv run uvicorn src.app:app --reload --host 127.0.0.1 --port 8000

lint:
	uv run ruff check src/
	uv run isort --check-only src/
	uv run ruff format --check src/

lint-fix:
	uv run ruff check --fix src/
	uv run isort src/
	uv run ruff format src/

format:
	uv run ruff format src/
