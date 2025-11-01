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

Start the development server:
```bash
make run
```

The API will be available at `http://127.0.0.1:8000`

Interactive API documentation (Swagger UI): `http://127.0.0.1:8000/docs`

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
