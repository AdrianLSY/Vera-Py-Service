from unittest import TestCase, main
from os import environ, getenv
from sqlalchemy import text
from core.database import Database

class TestDatabase(TestCase):
    """
    Integration test cases for the Database class using a real database.
    """
    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        """
        self.original_env = environ.copy()
        environ.update({"ENVIRONMENT": "test"})
        self.db = Database()
        self.db.initialize()

    def tearDown(self) -> None:
        try:
            self.db.teardown()
        except Exception:
            pass

        environ.clear()
        environ.update(self.original_env)

    def test_singleton(self):
        """
        Test that the Database class is a singleton.
        """
        db = Database()
        self.assertIs(db, self.db)

    def test_initialization(self):
        """
        Test that the Database class is initialized correctly.
        """
        assert self.db.host == getenv("POSTGRES_HOST")
        assert self.db.port == getenv("POSTGRES_PORT")
        assert self.db.username == getenv("POSTGRES_USER")
        assert self.db.password == getenv("POSTGRES_PASSWORD")
        assert self.db.environment == getenv("ENVIRONMENT")

    def test_deinitialization(self):
        """
        Test that the Database class is deinitialized correctly.
        """
        self.db.deinitialize()
        assert self.db.host == None
        assert self.db.port == None
        assert self.db.username == None
        assert self.db.password == None
        assert self.db.environment == None

    def test_correct_database(self):
        with self.db.session() as session:
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
        with self.db.session() as session:
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
        self.db.migrate()

        # Verify migration succeeded by checking alembic_version table has records
        with self.db.session() as session:
            result = session.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
                )
            )
            table_exists = result.scalar()
            self.assertTrue(table_exists, "alembic_version table should exist after migration")
        # Run teardown
        self.db.teardown()

        # Verify teardown succeeded by checking database is back to empty state
        with self.db.session() as session:
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
        with self.db.session() as session:
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
        with self.db.transaction() as session:
            session.execute(
                text(
                    "INSERT INTO test_transaction (value) VALUES ('success_value')"
                )
            )

        # Verify successful transaction data was committed
        with self.db.session() as session:
            result = session.execute(
                text(
                    "SELECT COUNT(*) FROM test_transaction WHERE value = 'success_value'"
                )
            )
            count = result.scalar()
            self.assertEqual(count, 1, "Data should be committed after successful transaction")

        # Test failed transaction - should rollback data
        with self.assertRaises(Exception):
            with self.db.transaction() as session:
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
        with self.db.session() as session:
            result = session.execute(
                text(
                    "SELECT COUNT(*) FROM test_transaction WHERE value = 'rollback_value'"
                )
            )
            count = result.scalar()
            self.assertEqual(count, 0, "Data should be rolled back after failed transaction")

        # Test manual rollback by raising custom exception
        with self.assertRaises(ValueError):
            with self.db.transaction() as session:
                session.execute(
                    text(
                        "INSERT INTO test_transaction (value) VALUES ('manual_rollback')"
                    )
                )
                raise ValueError("Manual rollback test")

        # Verify manual rollback occurred
        with self.db.session() as session:
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

if __name__ == '__main__':
    main()
