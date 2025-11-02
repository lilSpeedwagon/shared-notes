"""Tests for Snowflake ID generator."""

import pytest

import src.snowflake


def test_snowflake_init_with_worker_id() -> None:
    """Test Snowflake generator with custom worker ID."""
    generator = src.snowflake.SnowflakeGenerator(worker_id=42)
    assert generator.worker_id == 42


def test_snowflake_init_invalid_worker_id() -> None:
    """Test that invalid worker IDs raise ValueError."""
    with pytest.raises(ValueError, match="worker_id must be between 0 and 1023"):
        src.snowflake.SnowflakeGenerator(worker_id=-1)

    with pytest.raises(ValueError, match="worker_id must be between 0 and 1023"):
        src.snowflake.SnowflakeGenerator(worker_id=1024)


def test_generate_id() -> None:
    """Test generating a Snowflake ID."""
    generator = src.snowflake.SnowflakeGenerator(worker_id=0)
    snowflake_id = generator.generate_id()

    assert isinstance(snowflake_id, int)
    assert snowflake_id > 0
    assert snowflake_id.bit_length() <= 64


def test_generate_unique_ids() -> None:
    """Test that generated IDs are unique."""
    generator = src.snowflake.SnowflakeGenerator(worker_id=0)
    ids = {generator.generate_id() for _ in range(1000)}

    assert len(ids) == 1000  # All unique


def test_generate_sequential_ids() -> None:
    """Test that IDs generated in same millisecond are sequential."""
    generator = src.snowflake.SnowflakeGenerator(worker_id=0)
    id1 = generator.generate_id()
    id2 = generator.generate_id()
    id3 = generator.generate_id()

    # Should be in ascending order
    assert id2 > id1
    assert id3 > id2
