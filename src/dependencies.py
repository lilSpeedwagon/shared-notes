"""FastAPI dependencies for the application."""

import os

import fastapi
import sqlalchemy.ext.asyncio

from src.storage import base
from src.storage import db
from src.storage import factory

STORAGE_TYPE: base.StorageType = os.getenv('STORAGE_TYPE', 'sql').lower()


async def get_storage(
    db_session: sqlalchemy.ext.asyncio.AsyncSession = fastapi.Depends(db.get_db),
) -> base.PasteStorage:
    """
    Get the storage instance via dependency injection.

    The storage type is determined by the STORAGE_TYPE environment variable.
    - 'sql' (default): Uses PostgreSQL with the provided session
    - 'memory': Uses in-memory storage (session is ignored)

    Args:
        db_session: Database session from FastAPI dependency

    Returns:
        Storage instance based on configuration
    """
    if STORAGE_TYPE == 'sql':
        return factory.create_storage(storage_type='sql', session=db_session)
    else:
        return factory.create_storage(storage_type='memory')
