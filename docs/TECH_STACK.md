# Technology Stack and Decisions

This document captures current tech selections for the MVP and immediate next steps. Items may evolve; changes should be captured here and in ADRs if needed.

## Backend (Python)
- Python 3.13
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (models/validation)
- Pydantic Settings (configuration via environment variables)
- SQLAlchemy 2.x (database ORM/engine)
- Alembic (migrations)
- Pytest (unit tests)
- Linters: ruff, black, isort

## Storage
- PostgreSQL (primary data store; EBS-backed in MVP)
- Redis (read cache; optional in MVP)

## API
- REST under `/api/v1`
- JSON metadata, raw content endpoint with content negotiation
- Health endpoint `/healthz` (internal only)

## Frontend
- React
- Tailwind CSS
- Vite (build system)
- JavaScript linters/formatters: ESLint + Prettier (baseline); can refine rules later

## Containerization and Orchestration
- Docker
- Docker Compose (local and single-EC2 deployment)
- Traefik (reverse proxy, TLS, rate limiting)

## Observability
- Prometheus (metrics)
- Grafana (dashboards)
- Access logs via Traefik and application

## Security and Operations
- CORS restricted to the UI origin
- No paste content logging; minimal metadata logging
- TLS via Traefik (Let’s Encrypt) or Cloudflare

## Notes and Future Considerations
- Scale path: Postgres → RDS/Citus or CockroachDB; Redis → ElastiCache
- Large uploads: presigned S3 flow (post-MVP)
- Add ADRs as decisions evolve
