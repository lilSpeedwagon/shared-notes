"""Tests for Alembic database migrations."""

import pytest
from pytest_alembic import tests


@pytest.fixture
def alembic_config():
    """Override this fixture to configure the exact alembic context setup required."""
    return {'file': 'alembic.ini'}


@pytest.fixture
def alembic_engine(test_engine):
    """Use the test database engine for migration tests."""
    return test_engine


def test_single_head_revision(alembic_runner):
    """
    Test that there is only a single head revision.

    Prevents branching in migration history which can cause deployment issues.
    """
    tests.test_single_head_revision(alembic_runner)


def test_upgrade(alembic_runner):
    """
    Test that all migrations can be run (upgrade to head).

    Ensures migrations run without errors.
    """
    tests.test_upgrade(alembic_runner)


def test_model_definitions_match_ddl(alembic_runner):
    """
    Test that SQLAlchemy model definitions match the database schema.

    This is the most important test - it ensures that no schema changes
    were made to models without creating a corresponding migration.

    If this test fails, you need to create a new migration:
        make db-migrate message="description of changes"
    """
    tests.test_model_definitions_match_ddl(alembic_runner)


def test_up_down_consistency(alembic_runner):
    """
    Test that all migrations can be run up and down without errors.

    This verifies that:
    - All upgrade() functions work
    - All downgrade() functions work
    - Downgrade properly reverses upgrade
    """
    tests.test_up_down_consistency(alembic_runner)
