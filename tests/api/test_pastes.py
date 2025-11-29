"""Tests for paste creation and retrieval."""

import datetime

import httpx
import pytest

import tests.utils
from src.storage.db import models


@pytest.mark.asyncio
async def test_create_paste(async_client: httpx.AsyncClient) -> None:
    """Test creating a paste with valid data."""
    payload = {'content': 'Hello, World!', 'expires_in_seconds': 3600}

    response = await async_client.post('/api/v1/pastes', json=payload)

    assert response.status_code == 201
    assert response.json() == {
        'token': tests.utils.AnyStringOfLength(11),
        'expires_at': tests.utils.AnyFutureDatetime(min_seconds=3590, max_seconds=3610),
        'size_bytes': 13,
        'content_type': 'text/plain; charset=utf-8',
        'sha256': tests.utils.AnyString(),
    }


@pytest.mark.asyncio
async def test_create_paste_with_defaults(async_client: httpx.AsyncClient) -> None:
    """Test creating a paste with default expiration."""
    payload = {'content': 'Test content'}

    response = await async_client.post('/api/v1/pastes', json=payload)

    assert response.status_code == 201
    assert response.json() == {
        'token': tests.utils.AnyStringOfLength(11),
        'expires_at': tests.utils.AnyFutureDatetime(min_seconds=86390, max_seconds=86410),
        'size_bytes': 12,
        'content_type': 'text/plain; charset=utf-8',
        'sha256': tests.utils.AnyString(),
    }


@pytest.mark.asyncio
async def test_create_paste_empty_content(async_client: httpx.AsyncClient) -> None:
    """Test creating a paste with empty content returns 422."""
    payload = {'content': ''}

    response = await async_client.post('/api/v1/pastes', json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_paste_content_too_large(async_client: httpx.AsyncClient) -> None:
    """Test creating a paste with content exceeding max size returns 422."""
    payload = {'content': 'x' * 65537}  # Max is 65536

    response = await async_client.post('/api/v1/pastes', json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_paste_invalid_expiration(async_client: httpx.AsyncClient) -> None:
    """Test creating a paste with invalid expiration returns 422."""
    # Too short
    payload = {'content': 'test', 'expires_in_seconds': 30}
    response = await async_client.post('/api/v1/pastes', json=payload)
    assert response.status_code == 422

    # Too long
    payload = {'content': 'test', 'expires_in_seconds': 700000}
    response = await async_client.post('/api/v1/pastes', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_paste(async_client: httpx.AsyncClient) -> None:
    """Test retrieving a paste by token."""
    # Create a paste first
    create_payload = {'content': 'Retrieve me!', 'expires_in_seconds': 3600}
    create_response = await async_client.post('/api/v1/pastes', json=create_payload)
    assert create_response.status_code == 201
    create_data = create_response.json()
    token = create_data['token']

    # Retrieve the paste
    response = await async_client.get(f'/api/v1/pastes/{token}')

    assert response.status_code == 200
    assert response.json() == {
        'token': token,
        'content': 'Retrieve me!',
        'expires_at': create_data['expires_at'],
        'size_bytes': 12,
        'content_type': 'text/plain; charset=utf-8',
        'sha256': create_data['sha256'],
    }


@pytest.mark.asyncio
async def test_get_paste_not_found(async_client: httpx.AsyncClient) -> None:
    """Test retrieving a non-existent paste returns 404."""
    response = await async_client.get('/api/v1/pastes/nonexistent')

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_paste_expiration(async_client: httpx.AsyncClient, db_session) -> None:
    """Test that expired pastes cannot be retrieved."""

    # Create an expired paste directly in the database
    now = datetime.datetime.now(datetime.timezone.utc)
    expired_paste = models.Paste(
        token='expiredtest',
        snowflake_id=1234567890123456789,
        content='Expired content',
        content_type='text/plain; charset=utf-8',
        size_bytes=15,
        sha256='a' * 64,
        created_at=now - datetime.timedelta(hours=2),
        expires_at=now - datetime.timedelta(hours=1),  # Expired 1 hour ago
    )
    db_session.add(expired_paste)
    await db_session.commit()

    # Try to retrieve - should fail as expired
    response = await async_client.get('/api/v1/pastes/expiredtest')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_paste_content(async_client: httpx.AsyncClient) -> None:
    """Test retrieving raw paste content."""
    # Create a paste first
    create_payload = {'content': 'Raw content here!', 'expires_in_seconds': 3600}
    create_response = await async_client.post('/api/v1/pastes', json=create_payload)
    assert create_response.status_code == 201
    token = create_response.json()['token']
    sha256 = create_response.json()['sha256']

    # Retrieve the raw content
    response = await async_client.get(f'/api/v1/pastes/{token}/content')

    assert response.status_code == 200
    assert response.text == 'Raw content here!'
    assert response.headers['content-type'] == 'text/plain; charset=utf-8'
    assert response.headers['cache-control'] == 'no-store'
    assert response.headers['etag'] == f'"{sha256}"'


@pytest.mark.asyncio
async def test_get_paste_content_not_found(async_client: httpx.AsyncClient) -> None:
    """Test retrieving content for non-existent paste returns 404."""
    response = await async_client.get('/api/v1/pastes/nonexistent/content')

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_paste_content_expired(async_client: httpx.AsyncClient, db_session) -> None:
    """Test that expired paste content cannot be retrieved."""
    # Create an expired paste directly in the database
    now = datetime.datetime.now(datetime.timezone.utc)
    expired_paste = models.Paste(
        token='expiredcont',
        snowflake_id=1234567890123456790,
        content='Expired content',
        content_type='text/plain; charset=utf-8',
        size_bytes=15,
        sha256='b' * 64,
        created_at=now - datetime.timedelta(hours=2),
        expires_at=now - datetime.timedelta(hours=1),  # Expired 1 hour ago
    )
    db_session.add(expired_paste)
    await db_session.commit()

    # Try to retrieve content - should fail as expired
    response = await async_client.get('/api/v1/pastes/expiredcont/content')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_paste_content_with_unicode(async_client: httpx.AsyncClient) -> None:
    """Test retrieving paste content with UTF-8 characters."""
    # Create a paste with UTF-8 content
    content = 'Hello 世界 🌍 Emoji test!'
    create_payload = {'content': content, 'expires_in_seconds': 3600}
    create_response = await async_client.post('/api/v1/pastes', json=create_payload)
    assert create_response.status_code == 201
    token = create_response.json()['token']

    # Retrieve the raw content
    response = await async_client.get(f'/api/v1/pastes/{token}/content')

    assert response.status_code == 200
    assert response.text == content
    assert response.headers['content-type'] == 'text/plain; charset=utf-8'
