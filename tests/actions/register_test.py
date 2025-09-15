from unittest import TestCase, main
from os import getenv, environ
from core.database import Database
from actions.register import Register
from unittest.mock import MagicMock
from asyncio import run


class TestRegister(TestCase):
    """
    Integration test cases for the Database class using real database.
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        """
        # Set up test environment variables
        self.original_env = environ.copy()
        environ.update({"ENVIRONMENT": "test"})

        self.magic_mock = MagicMock()
        self.db = Database()
        self.db.initialize()
        # Skip migration for now to test connection
        # self.db.migrate()

    def tearDown(self) -> None:
        """
        Clean up after each test method.
        """
        # Restore original environment
        environ.clear()
        environ.update(self.original_env)
        # self.db.teardown()
        pass

    async def __test_register(self) -> None:
        """
        Test register action.
        """
        await Register(
            username = "testuser",
            name = "Test User",
            email = "testuser@example.com",
            phone_number = "+12345678901",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

    def test_register(self) -> None:
        """
        Test register action.
        """
        run(self.__test_register())

if __name__ == '__main__':
    main()
