"""Unit tests for storage layer."""

import datetime

import src.storage.memory
import tests.utils


async def test_create_paste() -> None:
    """Test creating and storing a paste."""
    storage = src.storage.memory.InMemoryPasteStorage()

    paste = await storage.create(
        content='Test content',
        expires_in_seconds=3600,
        content_type='text/plain; charset=utf-8',
    )

    assert paste.token == tests.utils.AnyStringOfLength(11)
    assert paste.content == 'Test content'
    assert paste.content_type == 'text/plain; charset=utf-8'
    assert paste.size_bytes == 12  # len('Test content'.encode('utf-8'))
    assert paste.sha256 == tests.utils.AnyString()
    assert len(paste.sha256) == 64
    assert paste.created_at == tests.utils.AnyRecentDatetime()

    # Verify expiration is approximately 3600 seconds in future
    assert paste.expires_at == tests.utils.AnyFutureDatetime(min_seconds=3590, max_seconds=3610)


async def test_create_paste_with_utf8_content() -> None:
    """Test creating a paste with UTF-8 content."""
    storage = src.storage.memory.InMemoryPasteStorage()

    paste = await storage.create(
        content='Hello 世界 🌍',
        expires_in_seconds=3600,
        content_type='text/plain; charset=utf-8',
    )

    assert paste.content == 'Hello 世界 🌍'
    # UTF-8 encoded size is larger than character count
    assert paste.size_bytes == len('Hello 世界 🌍'.encode('utf-8'))
    assert paste.size_bytes > len('Hello 世界 🌍')


async def test_get_existing_paste() -> None:
    """Test retrieving an existing non-expired paste."""
    storage = src.storage.memory.InMemoryPasteStorage()

    created = await storage.create(
        content='Retrievable content',
        expires_in_seconds=3600,
        content_type='text/plain; charset=utf-8',
    )

    retrieved = await storage.get(created.token)

    assert retrieved is not None
    assert retrieved.token == created.token
    assert retrieved.content == 'Retrievable content'
    assert retrieved.size_bytes == created.size_bytes
    assert retrieved.sha256 == created.sha256
    assert retrieved.expires_at == created.expires_at


async def test_get_nonexistent_paste() -> None:
    """Test retrieving a non-existent paste returns None."""
    storage = src.storage.memory.InMemoryPasteStorage()

    result = await storage.get('nonexistent')

    assert result is None


async def test_get_expired_paste() -> None:
    """Test that retrieving an expired paste returns None and removes it."""
    storage = src.storage.memory.InMemoryPasteStorage()

    # Create a paste
    paste = await storage.create(
        content='Will expire',
        expires_in_seconds=3600,
        content_type='text/plain; charset=utf-8',
    )

    # Manually expire it by setting expiration to the past
    paste.expires_at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)
    storage._pastes[paste.token] = paste

    # Try to retrieve - should return None
    result = await storage.get(paste.token)

    assert result is None
    # Verify it was cleaned up
    assert paste.token not in storage._pastes


async def test_create_multiple_pastes() -> None:
    """Test creating multiple pastes with unique tokens."""
    storage = src.storage.memory.InMemoryPasteStorage()

    paste1 = await storage.create(content='First', expires_in_seconds=3600)
    paste2 = await storage.create(content='Second', expires_in_seconds=3600)
    paste3 = await storage.create(content='Third', expires_in_seconds=3600)

    # All tokens should be unique
    assert paste1.token != paste2.token
    assert paste1.token != paste3.token
    assert paste2.token != paste3.token

    # All should be retrievable
    assert await storage.get(paste1.token) is not None
    assert await storage.get(paste2.token) is not None
    assert await storage.get(paste3.token) is not None


async def test_cleanup_expired() -> None:
    """Test manual cleanup of expired pastes."""
    storage = src.storage.memory.InMemoryPasteStorage()
    now = datetime.datetime.now(datetime.timezone.utc)

    # Create some pastes
    paste1 = await storage.create(content='Active 1', expires_in_seconds=3600)
    paste2 = await storage.create(content='Expired 1', expires_in_seconds=3600)
    paste3 = await storage.create(content='Expired 2', expires_in_seconds=3600)
    paste4 = await storage.create(content='Active 2', expires_in_seconds=3600)

    # Manually expire some pastes
    paste2.expires_at = now - datetime.timedelta(seconds=10)
    paste3.expires_at = now - datetime.timedelta(seconds=5)
    storage._pastes[paste2.token] = paste2
    storage._pastes[paste3.token] = paste3

    # Run cleanup
    removed_count = await storage.cleanup_expired()

    assert removed_count == 2
    # Active pastes should still exist
    assert await storage.get(paste1.token) is not None
    assert await storage.get(paste4.token) is not None
    # Expired pastes should be gone
    assert paste2.token not in storage._pastes
    assert paste3.token not in storage._pastes


async def test_cleanup_expired_with_no_expired() -> None:
    """Test cleanup when there are no expired pastes."""
    storage = src.storage.memory.InMemoryPasteStorage()

    paste1 = await storage.create(content='Active 1', expires_in_seconds=3600)
    paste2 = await storage.create(content='Active 2', expires_in_seconds=3600)

    removed_count = await storage.cleanup_expired()

    assert removed_count == 0
    assert await storage.get(paste1.token) is not None
    assert await storage.get(paste2.token) is not None


async def test_paste_size_calculation() -> None:
    """Test that paste size is correctly calculated in bytes."""
    storage = src.storage.memory.InMemoryPasteStorage()

    # ASCII content
    paste1 = await storage.create(content='abc', expires_in_seconds=3600)
    assert paste1.size_bytes == 3

    # UTF-8 content with multibyte characters
    paste2 = await storage.create(content='日本', expires_in_seconds=3600)
    assert paste2.size_bytes == len('日本'.encode('utf-8'))
    assert paste2.size_bytes > 2  # Each character is multiple bytes

    # Empty content
    paste3 = await storage.create(content='', expires_in_seconds=3600)
    assert paste3.size_bytes == 0
