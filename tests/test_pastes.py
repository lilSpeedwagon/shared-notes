"""Tests for paste creation and retrieval."""

import datetime

import httpx
import pytest


@pytest.mark.asyncio
async def test_create_paste(async_client: httpx.AsyncClient) -> None:
    """Test creating a paste with valid data."""
    payload = {'content': 'Hello, World!', 'expires_in_seconds': 3600}

    response = await async_client.post('/api/v1/pastes', json=payload)

    assert response.status_code == 201
    data = response.json()
    assert 'token' in data
    assert len(data['token']) == 11
    assert 'expires_at' in data
    assert data['size_bytes'] == len('Hello, World!'.encode('utf-8'))
    assert data['content_type'] == 'text/plain; charset=utf-8'
    assert 'sha256' in data


@pytest.mark.asyncio
async def test_create_paste_with_defaults(async_client: httpx.AsyncClient) -> None:
    """Test creating a paste with default expiration."""
    payload = {'content': 'Test content'}

    response = await async_client.post('/api/v1/pastes', json=payload)

    assert response.status_code == 201
    data = response.json()
    assert 'token' in data
    assert 'expires_at' in data


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
    token = create_response.json()['token']

    # Retrieve the paste
    response = await async_client.get(f'/api/v1/pastes/{token}')

    assert response.status_code == 200
    data = response.json()
    assert data['token'] == token
    assert data['content'] == 'Retrieve me!'
    assert data['size_bytes'] == len('Retrieve me!'.encode('utf-8'))
    assert 'expires_at' in data
    assert 'sha256' in data


@pytest.mark.asyncio
async def test_get_paste_not_found(async_client: httpx.AsyncClient) -> None:
    """Test retrieving a non-existent paste returns 404."""
    response = await async_client.get('/api/v1/pastes/nonexistent')

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_paste_expiration(async_client: httpx.AsyncClient) -> None:
    """Test that expired pastes cannot be retrieved."""
    # Create a paste that expires immediately (minimum is 60 seconds in real use)
    # For testing, we'll manipulate the storage directly
    import src.api.pastes
    import src.storage.memory

    storage = src.api.pastes.get_storage()

    # Create paste directly in storage with past expiration
    paste = storage.create(
        content='Expired content',
        expires_in_seconds=60,  # Will be in future
        content_type='text/plain; charset=utf-8',
    )

    # Manually set expiration to past
    paste.expires_at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)
    storage._pastes[paste.token] = paste

    # Try to retrieve - should fail as expired
    response = await async_client.get(f'/api/v1/pastes/{paste.token}')
    assert response.status_code == 404
