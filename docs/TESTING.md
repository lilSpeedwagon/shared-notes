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

import tests.utils

@pytest.mark.asyncio
async def test_feature_name(async_client: httpx.AsyncClient) -> None:
    """Brief description of what is being tested."""
    response = await async_client.get('/endpoint')
    
    # Check all relevant aspects in one test
    assert response.status_code == 200
    assert response.json() == {
        'expected': 'data',
        'expected_sting': tests.utils.AnyString(),
    }
```

### Type Hints

Always include type hints for:
- **Fixture parameters**: Specify the fixture type (e.g., `async_client: httpx.AsyncClient`)
- **Return type**: Use `-> None` for test functions
- **Variables**: Type hint local variables when type isn't obvious

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

## What to Test

### API Endpoints
For each endpoint, verify:
- Status codes (success and error cases)
- Response body structure and content
- Response headers (content-type, etc.)
- Error responses and validation

### Standalone Functions
- Check outputs with specified inputs
- Make sure no side effects
- Use parametrize instead of separate test cases

## CI/CD Integration

The project uses GitHub Actions for continuous integration. Tests and linters run automatically on:
- **Pull Requests**: Every PR to `main` or `dev` branches
- **Branch Pushes**: Direct pushes to `main` or `dev` branches

### Requirements

- All linters must pass (zero errors)
- All tests must pass (100% success rate)
- No changes to formatting required

PRs cannot be merged until all CI checks pass.
