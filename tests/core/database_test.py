from os import environ, getenv
from typing import Dict
from unittest import TestCase, main

from sqlalchemy import text

from core.database import Database, database


class TestDatabase(TestCase):
    """
    Integration test cases for the Database class using a real database.
    """
    original_env: Dict[str, str]  # type: ignore

    def setUp(self) -> None:  # type: ignore
        """
        Set up test fixtures before each test method.
        """
        self.original_env = environ.copy()
        environ.update({"ENVIRONMENT": "test"})
        database.initialize()

    def tearDown(self) -> None:  # type: ignore
        try:
            database.teardown()
        except Exception:
            pass

        try:
            database.deinitialize()
        except Exception:
            pass

        environ.clear()
        environ.update(self.original_env)

    def test_singleton(self):
        """
        Test that the Database class is a singleton.
        """
        # Test that multiple calls to Database() return the same instance
        db1 = Database()
        db2 = Database()
        self.assertIs(db1, db2)

    def test_initialization(self):
        """
        Test that the Database class is initialized correctly.
        """
        assert database.host == getenv("POSTGRES_HOST")
        assert database.port == getenv("POSTGRES_PORT")
        assert database.username == getenv("POSTGRES_USER")
        assert database.password == getenv("POSTGRES_PASSWORD")
        assert database.environment == getenv("ENVIRONMENT")

    def test_deinitialization(self):
        """
        Test that the Database class is deinitialized correctly.
        """
        database.deinitialize()
        assert database.host == None
        assert database.port == None
        assert database.username == None
        assert database.password == None
        assert database.environment == None

        # Reinitialize for subsequent tests
        database.initialize()

    def test_correct_database(self):
        with database.session() as session:
            result = session.execute(
                text(
                    "SELECT current_database();"
                )
            )
            current_database = result.scalar()
            assert current_database == environ.get("POSTGRES_DB_TEST")

    def  test_session_migration_and_teardown(self):
        """
        Test that the Database class can be migrated and torn down correctly.
        """
        # Check if alembic_version table exists and verify it's empty
        with database.session() as session:
            result = session.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
                )
            )
            table_exists = result.scalar()

            if table_exists:
                # If table exists, check that it has no records (empty database)
                result = session.execute(
                    text(
                        "SELECT COUNT(*) FROM alembic_version"
                    )
                )
                version_count = result.scalar()
                self.assertEqual(version_count, 0, "alembic_version table should be empty in clean database")

        # Run migration
        database.migrate()

        # Verify migration succeeded by checking alembic_version table has records
        with database.session() as session:
            result = session.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
                )
            )
            table_exists = result.scalar()
            self.assertTrue(table_exists, "alembic_version table should exist after migration")
        # Run teardown
        database.teardown()

        # Verify teardown succeeded by checking database is back to empty state
        with database.session() as session:
            result = session.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
                )
            )
            table_exists = result.scalar()

            if table_exists:
                # If table still exists, it should be empty after teardown
                result = session.execute(
                    text(
                        "SELECT COUNT(*) FROM alembic_version"
                    )
                )
                version_count = result.scalar()
                self.assertEqual(version_count, 0, "alembic_version table should be empty after teardown")

    def test_transaction(self):
        """
        Test that transactions handle both success and failure scenarios correctly.
        """
        # Create a temporary test table
        with database.session() as session:
            session.execute(
                text(
                    """
                    CREATE TEMPORARY TABLE test_transaction (
                    id SERIAL PRIMARY KEY,
                    value VARCHAR(50) UNIQUE
                    )
                    """
                )
            )
            session.commit()

        # Test successful transaction - should commit data
        with database.transaction() as session:
            session.execute(
                text(
                    "INSERT INTO test_transaction (value) VALUES ('success_value')"
                )
            )

        # Verify successful transaction data was committed
        with database.session() as session:
            result = session.execute(
                text(
                    "SELECT COUNT(*) FROM test_transaction WHERE value = 'success_value'"
                )
            )
            count = result.scalar()
            self.assertEqual(count, 1, "Data should be committed after successful transaction")

        # Test failed transaction - should rollback data
        with self.assertRaises(Exception):
            with database.transaction() as session:
                session.execute(
                    text(
                        "INSERT INTO test_transaction (value) VALUES ('rollback_value')"
                    )
                )
                # Force an exception by violating unique constraint
                session.execute(
                    text(
                        "INSERT INTO test_transaction (value) VALUES ('rollback_value')"
                    )
                )

        # Verify rollback occurred - 'rollback_value' should not exist
        with database.session() as session:
            result = session.execute(
                text(
                    "SELECT COUNT(*) FROM test_transaction WHERE value = 'rollback_value'"
                )
            )
            count = result.scalar()
            self.assertEqual(count, 0, "Data should be rolled back after failed transaction")

        # Test manual rollback by raising custom exception
        with self.assertRaises(ValueError):
            with database.transaction() as session:
                session.execute(
                    text(
                        "INSERT INTO test_transaction (value) VALUES ('manual_rollback')"
                    )
                )
                raise ValueError("Manual rollback test")

        # Verify manual rollback occurred
        with database.session() as session:
            result = session.execute(
                text(
                    "SELECT COUNT(*) FROM test_transaction WHERE value = 'manual_rollback'"
                )
            )
            count = result.scalar()
            self.assertEqual(count, 0, "Data should not exist after manual rollback")

            # Verify only successful transaction data remains
            result = session.execute(
                text(
                    "SELECT COUNT(*) FROM test_transaction"
                )
            )
            total_count = result.scalar()
            self.assertEqual(total_count, 1, "Only successful transaction data should remain")


if __name__ == "__main__":
    main()
