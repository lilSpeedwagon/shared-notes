# Notes Paste Bin — Requirements

This document defines functional and non-functional requirements for the Notes Paste Bin service. The scope is intentionally minimal for the MVP and expands with post-MVP features.

## Goals and Scope

- Provide a simple way to share plain-text documents via short links that expire automatically.
- Prioritize correctness, security, and simplicity over advanced features in MVP.

## Glossary

- Paste: A stored plain-text document.
- Short link: An auto-generated, URL-safe token used to retrieve a paste.
- TTL: Time-to-live; the duration after which a paste expires and becomes inaccessible.

## Out of Scope (MVP)

- Rich text, file attachments other than plain text
- User accounts, authentication, or roles
- Editing pastes after creation
- Search and listings of pastes
- Multi-tenancy or team features

---

## Functional Requirements — MVP

1) Create Paste
- As an anonymous user, I can submit plain text up to a maximum size limit.
- The system generates a short link and returns it with the server-side expiration time.
- The user can specify a custom expiration up to 7 days; presets are offered for convenience.

Acceptance Criteria
- On success, the response provides a short link, token, and absolute expiry timestamp.
- Empty input or input exceeding the size limit is rejected with a clear error message.
- Expiration can be set via presets (10 minutes, 1 hour, 24 hours, 7 days) or a custom value up to 7 days; default is 24 hours.

2) Retrieve Paste
- As any user with the short link, I can retrieve the exact original text until it expires.

Acceptance Criteria
- Retrieving by short link returns the original text as plain text by default.
- Expired or unknown tokens are not disclosed; the resource is treated as not available.
- Responses must discourage client-side caching for sensitive data (see NFRs).

3) Expiration
- Pastes automatically become inaccessible after TTL.

Acceptance Criteria
- Expired pastes are not retrievable.
- Background cleanup is not required in MVP, but expired pastes must never be served.

4) Health/Status
- The service exposes a minimal readiness/liveness indicator for deployment.

Acceptance Criteria
- A health indicator is available to signal process readiness/liveness.

5) Minimal UI (MVP)
- Provide a simple landing page to create a paste: a large text area, an expiration selector (presets and custom up to 7 days), and a create action.
- Provide a paste view page that displays the paste content and its remaining time until expiration.

Acceptance Criteria
- Users can create a paste from the landing page without authentication and receive a shareable link.
- Opening the shareable link shows the paste content and indicates its expiry/remaining time.

---

## Functional Requirements — Post-MVP (Backlog)

- Advanced expiration options (beyond 7 days, no-expiry modes)
- Password-protected pastes
- One-time view (burn after reading)
- Syntax highlighting (server-rendered HTML view) with XSS-safe rendering
- Optional raw download vs. rendered view toggle
- QR code for share links
- Paste deletion via admin or possession token
- Basic analytics (view count, last access time)
- Public API keys and rate tiers
- Abuse mitigation UI/captcha for suspicious behavior
- Admin console for moderation and purge

---

## Non-Functional Requirements — MVP

Security
- Input validation: reject binary content and enforce UTF-8.
- Output safety: serve raw text as text/plain; do not inline user content in HTML in MVP.
- Secrets management: do not expose secrets; configuration handling must be secure.
- Privacy: do not log paste contents; log only minimal metadata (token prefix, sizes, status codes).

Performance
- Maximum paste size: 64 KB (configurable).
- P50 create < 150 ms and P95 < 500 ms under light load (single instance).
- P50 retrieve < 100 ms and P95 < 400 ms for in-region clients.

Availability and Durability
- Single-region; target 99.5% monthly availability for MVP.
- Data durability sufficient for TTL; no long-term backups required for expired data.

Rate Limiting and Abuse Controls
- Basic per-IP rate limit: default 60 requests/minute (configurable), applied to create endpoints.
- Payload size checks MUST precede storage.

Observability
- Structured logs for requests, errors, and expiry outcomes.
- Basic metrics: requests, successes, failures, response times; health indicator.

Compliance and Legal
- No storage of personal data beyond transient IP and user agent in logs for security.
- Provide a simple acceptable use statement in README or landing page.

Operational
- Configuration defaults must be documented.
- Zero local persistence assumption allowed for MVP (in-memory or ephemeral store acceptable if it respects TTL); see Constraints.

---

## Constraints

- Baseline stack: Python 3.13 + FastAPI (see Architecture doc for details).
- No new third-party libraries without approval; prefer stdlib or already-approved deps.
- Hosting, storage, and CI/CD are defined in architecture/deployment docs; MVP may run single instance.
- The MVP has 0 to very low budget for hosting.

---

## Acceptance Test Outline (MVP)

- Successful create returns token, expiry, and retrieval URL for valid input.
- Invalid input (empty or >64 KB) is rejected with a clear error.
- Retrieving before expiry returns the original text as plain text.
- After expiry, retrieval is not possible.
- Health indicator is reachable and reports healthy when the service is running.
- Rate limit enforced on rapid create requests from same IP.

---

## Assumptions and Risks

- Anonymous usage requires stronger abuse controls; rate limits are essential.
- In-memory storage risks data loss on restarts; acceptable for MVP if clearly documented.
- Link guessing risk mitigated by sufficiently large token entropy (see Architecture).
- Potential legal risk if users upload prohibited content; require acceptable use statement and takedown process post-MVP.

---

## MVP Success Criteria

- Users can reliably create and share text via links that expire as configured.
- The system enforces size limits, TTL, and basic rate limiting.
- The service is operable with minimal logs/metrics and deployable via CI.
