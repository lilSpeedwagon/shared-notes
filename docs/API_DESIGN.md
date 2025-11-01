# API Design — Notes Paste Bin

Base path: `/api/v1`

Health: `/healthz` (internal only; not routed publicly)

## Conventions

- Content types
	- Requests: `application/json; charset=utf-8`
	- Responses: `application/json; charset=utf-8` unless noted; retrieval defaults to `text/plain; charset=utf-8`
- Time format: RFC 3339/ISO 8601 (UTC), e.g., `2025-10-31T12:00:00Z`
- Size limits: content up to 64 KiB (configurable)
- Expiration: custom up to 7 days (604800 seconds)
- Errors: unified JSON error body (see Error Model)
- Versioning: prefix all endpoints with `/api/v1`
- Separation: metadata and content use separate endpoints
- Storage modes: `inline` (DB) or `external` (e.g., S3) for large items
- Integrity: responses may include `ETag` header and `sha256` field in metadata

## Resources

### Create Paste

POST `/api/v1/pastes`

- Request (application/json)
    ```
    {
        "content": "string, required",
        "expires_in_seconds": 86400,
        "content_type": "text/plain; charset=utf-8",
        "filename": "optional.txt"
    }
    ```
- `content`: plain text (UTF-8), required, 1..65536 bytes
- `expires_in_seconds`: optional, integer in [60, 604800]; default 86400 (24h)
- `content_type`: optional, defaults to `text/plain; charset=utf-8` in MVP
- `filename`: optional, used for `Content-Disposition` when downloading

- Responses
	- 201 Created
		- Headers: `Location: /api/v1/pastes/{token}`
		- Body (application/json):
            ```
            {
                "token": "11-char base62",
                "url": "https://api.example.com/api/v1/pastes/abcDEF123xy",
                "expires_at": "2025-10-31T12:00:00Z",
                "size_bytes": 42,
                "content_type": "text/plain; charset=utf-8",
                "storage": "inline",
                "sha256": "b94d27b9934d3e08a52e52d7da7dabfa..."
            }
            ```
	- 400 Bad Request — invalid input (empty content, invalid expires_in_seconds)
	- 413 Payload Too Large — content exceeds size limit
	- 429 Too Many Requests — rate limited (edge/proxy)
	- 5xx — unexpected server error

- Error examples
    ```
    {
        "error": {
            "code": "invalid_request",
            "message": "expires_in_seconds must be between 60 and 604800"
        }
    }
    ```
    ```
    {
        "error": {
            "code": "payload_too_large",
            "message": "content exceeds 65536 bytes"
        }
    }
    ```

### Get Paste Metadata

GET `/api/v1/pastes/{token}`

- Responses
	- 200 OK (application/json)
        ```
        {
            "token": "abcDEF123xy",
            "expires_at": "2025-10-31T12:00:00Z",
            "size_bytes": 42,
            "content_type": "text/plain; charset=utf-8",
            "storage": "inline",
            "sha256": "b94d27b9934d3e08a52e52d7da7dabfa..."
        }
        ```
	- 404 Not Found — token unknown or expired (do not reveal existence)
	- 429 Too Many Requests — rate limited (edge/proxy)

### Get Paste Content

GET `/api/v1/pastes/{token}/content`

- Requests
	- Query params (optional): `disposition=inline|attachment`, `filename=name.ext`

- Responses
	- 200 OK (raw bytes) when storage is `inline`
		- Headers: `Content-Type` from metadata; optional `Content-Disposition`; `ETag` (recommended); `Cache-Control: no-store`
	- 302 Found when storage is `external`
		- Headers: `Location: <presigned URL>` (short-lived)
	- 404 Not Found — token unknown or expired (do not reveal existence)
	- 429 Too Many Requests — rate limited (edge/proxy)

### Health (internal only)

GET `/healthz`

- Not exposed publicly (proxy routing excludes it)
- 200 OK with minimal static payload (or empty)

## Error Model

We rely on the default FastAPI error model and common REST error codes such as:
- 404 Not Found
- 429 Too Many Tokens
- 500 Server Error
- etc

Common error codes
- `invalid_request`: payload validation failed
- `payload_too_large`: content size exceeded
- `not_found`: resource does not exist or expired
- `rate_limited`: too many requests
- `internal_error`: unexpected error

## Headers

- Creation
	- `Location`: canonical resource path `/api/v1/pastes/{token}`
- Rate limiting (if available from edge/proxy)
	- `Retry-After` on 429

## Notes

- Token format: 11-character Base62 string produced from a 64-bit Snowflake ID obfuscated via keyed Feistel; unique index on `token`.
- Health is internal-only; do not route through public domain.
- CORS: API only allows the configured UI origin.
