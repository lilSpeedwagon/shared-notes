# MVP Delivery Plan — Notes Paste Bin

A granular, incremental checklist to deliver the MVP.

## 0) Repository and Standards
- [x] Initialize Python project structure (`app/`, `tests/`, `infra/`, `docs/`)
- [x] Base tooling: formatter, linter, type checker (e.g., ruff, black, isort)
- [x] FastAPI skeleton with Uvicorn config
- [x] Basic Makefile / task runner commands
- [x] `.editorconfig` and coding standards reflected

## 1) API (In-Memory)
- [ ] Define Pydantic schemas for create request and responses
- [ ] Implement in-memory repository for pastes with TTL handling at read
- [ ] Implement token generation (Snowflake → Feistel → Base62)
- [ ] Endpoints:
	- [ ] POST `/api/v1/pastes`
	- [ ] GET `/api/v1/pastes/{token}` (metadata)
	- [ ] GET `/api/v1/pastes/{token}/content` (raw bytes)
	- [ ] GET `/healthz` (internal routing only)
- [ ] Error model and input validation (size limit, expires range)
- [ ] CORS for future UI origin

## 2) Tests
- [ ] Unit tests: token generator, validators, repository behavior
- [ ] API tests: happy paths, validation, expiry, 404 semantics
- [ ] Performance smoke: basic latency check for create/retrieve

## 3) CI/CD (GitHub Actions)
- [ ] Lint + type check + tests on PR
- [ ] Build API Docker image on main
- [ ] (Optional) Publish image to GHCR

## 4) Database Integration (PostgreSQL)
- [ ] DB schema (`pastes` with `id`, `token`, `content`, `created_at`, `expires_at`)
- [ ] Migration setup (Alembic)
- [ ] SQL repository with read-before-expiry semantics
- [ ] Config switch: in-memory vs Postgres
- [ ] Indexes: `token` (unique)

## 5) UI (React + Tailwind)
- [ ] Create paste page: textarea, expiration selector, submit
- [ ] View paste page: metadata + content retrieval, expiry indicator
- [ ] Build pipeline; serve separately; CORS configured

## 6) Cache (Redis — read cache only)
- [ ] Integrate Redis client (optional for MVP completion)
- [ ] Cache read-through for content by token with short TTL
- [ ] Config flag to enable/disable cache

## 7) Local Orchestration (Docker Compose)
- [ ] Compose services: traefik, api, postgres (EBS-mapped volume path placeholder), redis
- [ ] Traefik TLS (LE/Cloudflare), route rules, per-route rate limits
- [ ] Health checks for services

## 8) Deployment (Single EC2)
- [ ] Provision EC2 and security groups (Cloudflare/Tunnel choice noted)
- [ ] Install Docker + Compose; deploy stack
- [ ] DNS via Cloudflare; TLS termination via Traefik
- [ ] Document manual steps in `docs/DEPLOYMENT.md`

## 9) Monitoring (Prometheus + Grafana)
- [ ] Exporter for FastAPI metrics (Prometheus client)
- [ ] Compose stack: prometheus + grafana (basic dashboards)
- [ ] Uptime/health probe (Cloudflare health checks or external)

## 10) Hardening and Cleanup
- [ ] Logs: avoid content logging; redact sensitive fields
- [ ] Security headers on content endpoints; `Cache-Control: no-store`
- [ ] Review limits and Traefik rate limits per path
- [ ] Final pass against `docs/REQUIREMENTS.md` and `docs/API_DESIGN.md`

---

Owner can check off items incrementally. Keep PRs small and focused.
