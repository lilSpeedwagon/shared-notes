# Testing Strategy

This document defines the testing approach and standards for the Shared Notes project.

## Testing Principles

1. **One test per feature** - Each test should verify a complete feature/endpoint behavior
2. **No test classes** - Use simple test functions instead of test classes
3. **Comprehensive assertions** - A single test should check all relevant aspects (status code, body, headers, etc.)
4. **Async by default** - Use async tests with `httpx.AsyncClient` for API endpoints
5. **Clear test names** - Use descriptive function names that explain what is being tested
6. **Type hints required** - Always use type hints for function parameters and return types

## Test Structure

```
tests/
├── __init__.py          # Package marker
├── conftest.py          # Shared fixtures (client, async_client)
└── test_*.py            # Test modules organized by feature
```

## Writing Tests

### Test Function Format

```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_feature_name(async_client: httpx.AsyncClient) -> None:
    """Brief description of what is being tested."""
    response = await async_client.get('/endpoint')
    
    # Check all relevant aspects in one test
    assert response.status_code == 200
    assert response.json() == {'expected': 'data'}
    assert 'application/json' in response.headers['content-type']
```

### Type Hints

Always include type hints for:
- **Fixture parameters**: Specify the fixture type (e.g., `async_client: httpx.AsyncClient`)
- **Return type**: Use `-> None` for test functions
- **Variables**: Type hint local variables when type isn't obvious

**Example:**
```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_create_paste(async_client: httpx.AsyncClient) -> None:
    """Test paste creation with valid data."""
    payload: dict[str, str | int] = {
        'content': 'test content',
        'expires_in_seconds': 3600,
    }
    response = await async_client.post('/api/v1/pastes', json=payload)
    
    assert response.status_code == 201
```

### Fixtures Available

- **`async_client`** - Async HTTPX client for testing endpoints
- **`client`** - Synchronous FastAPI TestClient (use only if needed)

### Example: Health Check Test

```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_health_check(async_client: httpx.AsyncClient) -> None:
    """Test that health check endpoint works correctly."""
    response = await async_client.get('/healthz')
    
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}
    assert 'application/json' in response.headers['content-type']
```

## Test Organization

### Do ✓
- Use descriptive test function names: `test_create_paste_with_valid_data`
- Group related assertions in a single test
- Test the complete behavior of an endpoint
- Use async tests for API endpoints
- Keep tests focused on one feature
- Always add type hints for fixtures and return types

### Don't ✗
- Don't use test classes
- Don't split one feature into multiple micro-tests
- Don't test the same thing multiple ways
- Don't over-mock - use real FastAPI test clients

## Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_health.py

# Run specific test function
uv run pytest tests/test_health.py::test_health_check
```

## Test Coverage Goals

- **MVP**: Minimum 80% coverage for core endpoints
- **Post-MVP**: 90%+ coverage including edge cases

## What to Test

### API Endpoints
For each endpoint, verify:
- Status codes (success and error cases)
- Response body structure and content
- Response headers (content-type, etc.)
- Error responses and validation

### Example Test Coverage
- `POST /api/v1/pastes` - Create paste with valid/invalid data
- `GET /api/v1/pastes/{token}` - Retrieve existing/expired/non-existent paste
- `GET /healthz` - Health check returns correct status

## CI/CD Integration

The project uses GitHub Actions for continuous integration. Tests and linters run automatically on:
- **Pull Requests**: Every PR to `main` or `dev` branches
- **Branch Pushes**: Direct pushes to `main` or `dev` branches

### What Runs in CI

1. **Linters**:
   - `ruff check` - Code quality checks
   - `isort --check-only` - Import sorting verification
   - `ruff format --check` - Code formatting verification

2. **Tests**:
   - All pytest tests with verbose output
   - Tests must pass before code can be merged

### Workflow File

See `.github/workflows/ci.yml` for the complete CI configuration.

### Requirements

- All linters must pass (zero errors)
- All tests must pass (100% success rate)
- No changes to formatting required

PRs cannot be merged until all CI checks pass.

## Troubleshooting

### Async Tests Not Running
Ensure `pytest-asyncio` is installed and `asyncio_mode = "auto"` is set in `pyproject.toml`.

### Import Errors
Make sure the project root is in Python path. Tests import from `src.app`, not relative imports.

### Test Client Issues
Use `httpx.AsyncClient` with `ASGITransport` for async tests, or `fastapi.testclient.TestClient` for sync tests.

