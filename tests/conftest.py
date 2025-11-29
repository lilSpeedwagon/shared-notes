"""Pytest configuration and fixtures for API tests."""

import collections.abc
import os

import fastapi.testclient
import httpx
import pytest
import sqlalchemy
import sqlalchemy.ext.asyncio

import src.app
import src.storage.db
import src.storage.db.models  # noqa: F401 - Import models for table creation
from alembic import command
from alembic.config import Config as AlembicConfig

# Test database configuration from environment
TEST_DB_NAME = 'shared_notes_test'
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

# Database URLs
POSTGRES_ROOT_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres'
TEST_DATABASE_URL = (
    f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{TEST_DB_NAME}'
)

# Override DATABASE_URL for test environment
os.environ['DATABASE_URL'] = TEST_DATABASE_URL


@pytest.fixture(scope='session', autouse=True)
def setup_test_database():
    """
    Session-scoped fixture to setup and teardown test database.

    This runs once per test session and:
    1. Drops existing test database if it exists
    2. Creates a fresh test database
    3. Runs Alembic migrations to setup schema
    4. Yields to run all tests
    5. Downgrades all migrations
    6. Drops the test database

    This ensures complete isolation from development database.
    """
    # Create sync engine for database management operations
    sync_engine = sqlalchemy.create_engine(POSTGRES_ROOT_URL, isolation_level='AUTOCOMMIT')

    # Drop test database if exists
    with sync_engine.connect() as conn:
        conn.execute(sqlalchemy.text(f'DROP DATABASE IF EXISTS {TEST_DB_NAME}'))
        conn.execute(sqlalchemy.text(f'CREATE DATABASE {TEST_DB_NAME}'))

    # Run Alembic migrations using Alembic API
    alembic_cfg = AlembicConfig('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', TEST_DATABASE_URL.replace('+asyncpg', ''))
    command.upgrade(alembic_cfg, 'head')

    # Yield to run tests
    yield

    # Downgrade all migrations using Alembic API
    command.downgrade(alembic_cfg, 'base')

    # Drop test database using SQLAlchemy
    sync_engine = sqlalchemy.create_engine(POSTGRES_ROOT_URL, isolation_level='AUTOCOMMIT')
    with sync_engine.connect() as conn:
        # Terminate existing connections
        conn.execute(
            sqlalchemy.text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
              AND pid <> pg_backend_pid()
        """)
        )
        conn.execute(sqlalchemy.text(f'DROP DATABASE IF EXISTS {TEST_DB_NAME}'))


@pytest.fixture(scope='session')
def test_engine():
    """
    Create a test database engine for the entire test session.

    This engine connects to the test database created by setup_test_database fixture.
    """
    return sqlalchemy.ext.asyncio.create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=sqlalchemy.pool.NullPool,
    )


@pytest.fixture(autouse=True)
async def cleanup_tables(test_engine):
    """
    Cleanup all table data after each test for isolation.

    This fixture runs automatically after every test and truncates
    all tables to ensure test isolation without dropping/recreating schema.

    Uses SQLAlchemy metadata to get all tables dynamically.
    """
    yield  # Let the test run first

    # Cleanup after test
    async with test_engine.begin() as conn:
        for table in reversed(src.storage.db.Base.metadata.sorted_tables):
            await conn.execute(sqlalchemy.text(f'TRUNCATE TABLE {table.name} CASCADE'))


@pytest.fixture
def client() -> fastapi.testclient.TestClient:
    """Create a test client for the FastAPI app."""
    return fastapi.testclient.TestClient(src.app.app)


@pytest.fixture
async def async_client(
    test_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> collections.abc.AsyncGenerator[httpx.AsyncClient, None]:
    """
    Create an async test client with test database.

    Overrides the database dependency to use test database engine.
    """

    async def override_get_db():
        async_session = sqlalchemy.ext.asyncio.async_sessionmaker(
            test_engine,
            class_=sqlalchemy.ext.asyncio.AsyncSession,
            expire_on_commit=False,
        )
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    # Override the database dependency
    src.app.app.dependency_overrides[src.storage.db.get_db] = override_get_db

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=src.app.app),
        base_url='http://test',
    ) as client:
        yield client

    # Clear overrides after test
    src.app.app.dependency_overrides.clear()


@pytest.fixture
async def db_session(
    test_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> collections.abc.AsyncGenerator[sqlalchemy.ext.asyncio.AsyncSession, None]:
    """
    Provide a database session for tests that need to directly manipulate data.

    This session uses the same test database as async_client.
    """
    async_session = sqlalchemy.ext.asyncio.async_sessionmaker(
        test_engine,
        class_=sqlalchemy.ext.asyncio.AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
        await session.commit()


