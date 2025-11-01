.PHONY: run install dev

install:
	uv sync

dev:
	uv sync --extra dev

run:
	uv run uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
