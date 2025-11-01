"""Pytest configuration and fixtures for API tests."""

import collections.abc

import fastapi.testclient
import httpx
import pytest

import src.app


@pytest.fixture
def client() -> fastapi.testclient.TestClient:
    """Create a test client for the FastAPI app."""
    return fastapi.testclient.TestClient(src.app.app)


@pytest.fixture
async def async_client() -> collections.abc.AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=src.app.app),
        base_url='http://test',
    ) as client:
        yield client
