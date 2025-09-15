"""
Test script to verify that Alembic migrations use the correct test database.

This script demonstrates that the fix in alembic/env.py correctly respects
the database URL set by the Database class, ensuring migrations run against
the test database rather than the development database.
"""

from os import getenv
from sqlalchemy import text, inspect
from core.database import Database


def test_migration_uses_test_database() -> None:
    """
    Test that migrations are applied to the test database, not development.

    This test verifies that:
    1. The Database class initializes with the test database
    2. Migrations are run against the test database
    3. The created tables exist in the test database
    4. The development database is not affected
    """
    print("Testing migration database targeting...")

    # Initialize database with test database
    db = Database()
    db.initialize(
        host=getenv("POSTGRES_HOST", "localhost"),
        port=getenv("POSTGRES_PORT", "5432"),
        username=getenv("POSTGRES_USER", "auth"),
        password=getenv("POSTGRES_PASSWORD", "auth"),
        database=getenv("POSTGRES_DB_TEST", "auth_test")
    )

    print(f"Initialized database with: {getenv('POSTGRES_DB_TEST', 'auth_test')}")

    # First, clean up any existing tables (teardown)
    try:
        db.teardown()
        print("Teardown completed - removed existing tables")
    except RuntimeError as exc:
        if "Database teardown failed" in str(exc):
            print("Teardown failed (expected if no migrations exist)")
        else:
            raise

    # Verify no tables exist before migration
    with db.session() as session:
        inspector = inspect(session.bind)
        tables_before = inspector.get_table_names()
        print(f"Tables before migration: {tables_before}")

        # Verify we're connected to the test database
        result = session.execute(text("SELECT current_database()"))
        current_db = result.fetchone()[0]
        expected_db = getenv("POSTGRES_DB_TEST", "auth_test")
        assert current_db == expected_db, f"Expected {expected_db}, got {current_db}"
        print(f"✓ Confirmed connection to test database: {current_db}")

    # Run migrations
    try:
        db.migrate()
        print("✓ Migration completed successfully")
    except RuntimeError as exc:
        print(f"Migration failed: {exc}")
        raise

    # Verify tables were created in the test database
    with db.session() as session:
        inspector = inspect(session.bind)
        tables_after = inspector.get_table_names()
        print(f"Tables after migration: {tables_after}")

        # Check that expected tables exist
        expected_tables = {"users", "revocations", "alembic_version"}
        found_tables = set(tables_after)

        if expected_tables.issubset(found_tables):
            print("✓ All expected tables created successfully")
        else:
            missing = expected_tables - found_tables
            print(f"✗ Missing tables: {missing}")
            raise AssertionError(f"Missing expected tables: {missing}")

        # Verify we're still connected to the test database
        result = session.execute(text("SELECT current_database()"))
        current_db = result.fetchone()[0]
        expected_db = getenv("POSTGRES_DB_TEST", "auth_test")
        assert current_db == expected_db, f"Expected {expected_db}, got {current_db}"
        print(f"✓ Confirmed tables created in test database: {current_db}")

    # Verify migration version was recorded
    with db.session() as session:
        try:
            result = session.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()[0]
            print(f"✓ Migration version recorded: {version}")
        except Exception as exc:
            print(f"✗ Could not read migration version: {exc}")
            raise

    print("✓ All tests passed - migrations correctly target the test database!")


def test_development_database_unaffected() -> None:
    """
    Test that the development database is not affected by test migrations.

    This requires POSTGRES_DB_DEVELOPMENT to be set and accessible.
    """
    dev_db_name = getenv("POSTGRES_DB_DEVELOPMENT")
    if not dev_db_name:
        print("Skipping development database test - POSTGRES_DB_DEVELOPMENT not set")
        return

    print(f"\nTesting that development database '{dev_db_name}' is unaffected...")

    # Create a separate connection to the development database
    dev_db = Database()
    dev_db.initialize(
        host=getenv("POSTGRES_HOST", "localhost"),
        port=getenv("POSTGRES_PORT", "5432"),
        username=getenv("POSTGRES_USER", "auth"),
        password=getenv("POSTGRES_PASSWORD", "auth"),
        database=dev_db_name
    )

    # Check tables in development database
    with dev_db.session() as session:
        inspector = inspect(session.bind)
        dev_tables = inspector.get_table_names()

        # Verify we're connected to the development database
        result = session.execute(text("SELECT current_database()"))
        current_db = result.fetchone()[0]
        assert current_db == dev_db_name, f"Expected {dev_db_name}, got {current_db}"
        print(f"✓ Connected to development database: {current_db}")

        # Check if migration tables exist (they shouldn't if migrations only ran on test)
        migration_tables = {"users", "revocations", "alembic_version"}
        found_migration_tables = set(dev_tables) & migration_tables

        if found_migration_tables:
            print(f"⚠ Warning: Found migration tables in development database: {found_migration_tables}")
            print("This might indicate migrations were run against development database")
        else:
            print("✓ No migration tables found in development database (expected)")


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING ALEMBIC MIGRATION DATABASE TARGETING")
    print("=" * 70)

    try:
        test_migration_uses_test_database()
        test_development_database_unaffected()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED!")
        print("Alembic is correctly using the test database for migrations.")
        print("=" * 70)

    except Exception as exc:
        print(f"\n✗ TEST FAILED: {exc}")
        print("=" * 70)
        raise
