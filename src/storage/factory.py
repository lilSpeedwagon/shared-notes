"""Factory for creating storage instances based on configuration."""

import sqlalchemy.ext.asyncio

import src.storage.base
import src.storage.memory
import src.storage.sql


def create_storage(
    storage_type: src.storage.base.StorageType,
    session: sqlalchemy.ext.asyncio.AsyncSession | None = None,
    worker_id: int = 0,
) -> src.storage.base.PasteStorage:
    """
    Create a storage instance based on type.

    Args:
        storage_type: Type of storage ('sql' or 'memory')
        session: SQLAlchemy async session (required only for SQL storage)
        worker_id: Worker ID for Snowflake generator

    Returns:
        Storage instance

    Raises:
        ValueError: If storage_type is 'sql' but no session is provided
    """
    if storage_type == 'sql':
        if session is None:
            raise ValueError("SQL storage requires a database session")
        return src.storage.sql.SQLPasteStorage(session=session, worker_id=worker_id)
    elif storage_type == 'memory':
        return src.storage.memory.InMemoryPasteStorage(worker_id=worker_id)
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
