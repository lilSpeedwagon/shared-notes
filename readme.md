# Shared Notes

A simple notes sharing service (paste bin). The main aim of this project is to learn the AI agent capabilities when building a software product.

## Documentation

- [Requirements](/docs/REQUIREMENTS.md)
- [Architecture](/docs/ARCHITECTURE.md)
- [API](/docs/API_DESIGN.md)
- [Tech Stack](/docs/TECH_STACK.md)
- [Testing](/docs/TESTING.md)
- [MVP Road Map](/docs/MVP_PLAN.md)

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver

## Local Setup

1. Install dependencies:
```bash
make install
```

Or with dev dependencies:
```bash
make dev
```

## Running Local App

### Option 1: Direct Python (In-Memory Storage)

Start the development server with in-memory storage:
```bash
make run
```

The API will be available at `http://127.0.0.1:8000`

Interactive API documentation (Swagger UI): `http://127.0.0.1:8000/docs`

### Option 2: Docker Compose (PostgreSQL Storage)

Start the full stack with PostgreSQL:

```bash
make docker-up
```

The API will be available at `http://127.0.0.1:8000`

### Run Alembic migrations

```bash
# Apply database migrations
make db-upgrade

# Create a new migration (after modifying models)
make db-migrate message="description of changes"

# Stop and completely remove database (including all data)
make docker-clean
```

## Testing

Run tests:
```bash
make test
```

Run tests with coverage:
```bash
make test-cov
```

See [Testing Documentation](/docs/TESTING.md) for detailed testing guidelines.

## CI/CD

The project uses GitHub Actions for continuous integration. The CI pipeline automatically runs on:
- Pull requests to `main` or `dev` branches
- Direct pushes to `main` or `dev` branches

The pipeline runs:
- Linters (ruff, isort)
- Code formatting checks
- All tests

See `.github/workflows/ci.yml` for the full configuration.
