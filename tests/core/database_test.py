from unittest import TestCase, main
from os import environ, getenv
from sqlalchemy import text
from core.database import Database

class TestDatabase(TestCase):
    """
    Integration test cases for the Database class using real database.
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

    def test_migration_and_teardown(self):
        """
        Test that the Database class can be migrated and torn down correctly.
        """
        # First ensure we start from a clean state by running teardown
        try:
            self.db.teardown()
        except RuntimeError:
            # Ignore if teardown fails (no migrations to tear down)
            pass

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
                result = session.execute(text("SELECT COUNT(*) FROM alembic_version"))
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

            # Check that migration was recorded
            result = session.execute(text("SELECT COUNT(*) FROM alembic_version"))
            version_count = result.scalar()
            self.assertGreater(version_count, 0, "Should have at least one migration version recorded")

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
                result = session.execute(text("SELECT COUNT(*) FROM alembic_version"))
                version_count = result.scalar()
                self.assertEqual(version_count, 0, "alembic_version table should be empty after teardown")


if __name__ == '__main__':
    main()
