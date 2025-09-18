from asyncio import run
from os import environ, getenv
from typing import Any, Dict, cast
from unittest import TestCase, main
from unittest.mock import MagicMock

from actions.delete import Delete
from actions.login import Login
from actions.register import Register
from core.database import database
from models.user import User


class DeleteTest(TestCase):
    """
    Integration test cases for the Delete action using real database.
    """
    original_env: Dict[str, str]  # type: ignore
    magic_mock: MagicMock  # type: ignore
    jwt_secret: str  # type: ignore

    def setUp(self) -> None:  # type: ignore
        """
        Set up test fixtures before each test method.
        """
        # Set up test environment variables
        self.original_env = environ.copy()
        environ.update({"ENVIRONMENT": "test"})

        self.magic_mock = MagicMock()

        # Initialize the global database instance used by actions
        database.initialize()
        database.migrate()

        self.jwt_secret = getenv("JWT_SECRET")

        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is not set")

    def tearDown(self) -> None:  # type: ignore
        """
        Clean up after each test method.
        """
        # Clean up global database instance if it's initialized
        try:
            database.teardown()
            database.deinitialize()
        except RuntimeError:
            # Database was already deinitialized, ignore
            pass

        # Restore original environment
        environ.clear()
        environ.update(self.original_env)

    async def __test_delete_user_with_jwt(self) -> None:
        response = await Register(
            name = "Test User JWT",
            username = "testuser_jwt",
            email = "testuser_jwt@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        if response.fields is None:
            raise ValueError(f"Register failed: {response.message}")

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        # Verify user exists and is not deleted
        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_jwt"
            ).first()
            assert user is not None
            assert user.deleted_at is None

        response = await Delete(
            jwt = jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User deleted successfully"
        assert response.fields == None

        # Verify user is soft deleted
        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_jwt"
            ).first()
            assert user is not None
            assert user.deleted_at is not None

        # Verify user cannot login after deletion
        response = await Login(
            username = "testuser_jwt",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert response.status_code == 404
        assert response.message == "User not found"

    def test_delete_user_with_jwt(self) -> None:
        run(self.__test_delete_user_with_jwt())

    async def __test_delete_user_with_user_id(self) -> None:
        response = await Register(
            name = "Test User ID",
            username = "testuser_id",
            email = "testuser_id@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        # Get user_id from database
        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_id"
            ).first()
            user_id = user.id  # type: ignore

        # Verify user exists and is not deleted
        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_id"
            ).first()
            assert user is not None
            assert user.deleted_at is None

        response = await Delete(
            user_id = user_id
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User deleted successfully"
        assert response.fields == None

        # Verify user is soft deleted
        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_id"
            ).first()
            assert user is not None
            assert user.deleted_at is not None

        # Verify user cannot login after deletion
        response = await Login(
            username = "testuser_id",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert response.status_code == 404
        assert response.message == "User not found"

    def test_delete_user_with_user_id(self) -> None:
        run(self.__test_delete_user_with_user_id())

    async def __test_delete_user_with_jwt_and_user_id_consistency(self) -> None:
        response = await Register(
            name = "Test Consistency",
            username = "testuser_consistency",
            email = "testuser_consistency@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        if response.fields is None:
            raise ValueError(f"Register failed: {response.message}")

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        # Get user_id from database
        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_consistency"
            ).first()
            user_id = user.id  # type: ignore

        # Verify user exists and is not deleted
        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_consistency"
            ).first()
            assert user is not None
            assert user.deleted_at is None

        # Test with consistent JWT and user_id
        response = await Delete(
            jwt = jwt,
            user_id = user_id
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User deleted successfully"

        # Verify user is soft deleted
        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_consistency"
            ).first()
            assert user is not None
            assert user.deleted_at is not None

    def test_delete_user_with_jwt_and_user_id_consistency(self) -> None:
        run(self.__test_delete_user_with_jwt_and_user_id_consistency())

    async def __test_delete_user_with_jwt_and_user_id_inconsistency(self) -> None:
        response = await Register(
            name = "Test Inconsistency",
            username = "testuser_inconsistency",
            email = "testuser_inconsistency@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        if response.fields is None:
            raise ValueError(f"Register failed: {response.message}")

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        # Test with inconsistent JWT and user_id (different user_id)
        response = await Delete(
            jwt = jwt,
            user_id = 99999  # Different user_id
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 401
        assert response.message == "user id is not consistent between JWT and user_id"

    def test_delete_user_with_jwt_and_user_id_inconsistency(self) -> None:
        run(self.__test_delete_user_with_jwt_and_user_id_inconsistency())

    async def __test_delete_user_without_jwt_or_user_id(self) -> None:
        response = await Delete().run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 400
        assert response.message == "Either JWT or user_id must be provided"

    def test_delete_user_without_jwt_or_user_id(self) -> None:
        run(self.__test_delete_user_without_jwt_or_user_id())

    async def __test_delete_nonexistent_user(self) -> None:
        response = await Delete(
            user_id = 99999
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 404
        assert response.message == "User not found"

    def test_delete_nonexistent_user(self) -> None:
        run(self.__test_delete_nonexistent_user())

    async def __test_delete_already_deleted_user(self) -> None:
        response = await Register(
            name = "Test Already Deleted",
            username = "testuser_already_deleted",
            email = "testuser_already_deleted@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        if response.fields is None:
            raise ValueError(f"Register failed: {response.message}")

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        # Delete user first time
        response = await Delete(
            jwt = jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User deleted successfully"

        # Try to delete again
        response = await Delete(
            jwt = jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 404
        assert response.message == "User not found"

    def test_delete_already_deleted_user(self) -> None:
        run(self.__test_delete_already_deleted_user())

    async def __test_delete_user_with_invalid_jwt(self) -> None:
        response = await Delete(
            jwt = "invalid.jwt.token"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 401
        assert "Invalid token" in response.message

    def test_delete_user_with_invalid_jwt(self) -> None:
        run(self.__test_delete_user_with_invalid_jwt())


if __name__ == "__main__":
    main()
