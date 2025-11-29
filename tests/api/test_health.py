"""Tests for health check endpoint."""

import httpx
import pytest


@pytest.mark.asyncio
async def test_health_check(async_client: httpx.AsyncClient) -> None:
    """Test that health check endpoint works correctly."""
    response = await async_client.get('/healthz')

    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}
    assert 'application/json' in response.headers['content-type']
