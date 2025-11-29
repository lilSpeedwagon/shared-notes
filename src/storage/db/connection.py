"""Database connection and session management."""

import os

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

DATABASE_URL = os.getenv('DATABASE_URL')

engine = sqlalchemy.ext.asyncio.create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = sqlalchemy.ext.asyncio.async_sessionmaker(
    engine,
    class_=sqlalchemy.ext.asyncio.AsyncSession,
    expire_on_commit=False,
)


# Dependency for FastAPI
async def get_db() -> sqlalchemy.ext.asyncio.AsyncSession:
    """
    Dependency that provides a database session.

    Usage in FastAPI:
        @app.get('/items')
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Base class for SQLAlchemy models
Base = sqlalchemy.orm.declarative_base()
