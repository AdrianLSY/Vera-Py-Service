from asyncio import run
from os import environ, getenv
from typing import Any, Dict, cast
from unittest import TestCase, main
from unittest.mock import MagicMock

from actions.edit import Edit
from actions.login import Login
from actions.register import Register
from core.action_response import ActionResponse
from core.database import Database, database
from models.user import User


class TestEdit(TestCase):
    """
    Integration test cases for the Database class using real database.
    """
    original_env: Dict[str, str]  # type: ignore
    magic_mock: MagicMock  # type: ignore
    jwt_secret: str  # type: ignore
    register_jwt: str  # type: ignore
    register_claims: Dict[str, Any]  # type: ignore
    login_jwt: str  # type: ignore
    login_claims: Dict[str, Any]  # type: ignore
    jwt: str  # type: ignore

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

    async def __test_edit_user(self) -> None:
        response = await Register(
            name = "Test User",
            username = "testuser",
            email = "testuser@example.com",
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

        response = await Edit(
            jwt = jwt,
            name = "Edited User",
            username = "editeduser",
            email = "editeduser@example.com",
            phone_number = "+12123451234",
            password = "password456"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User updated successfully"
        assert response.fields == None

        with database.session() as session:
            user = session.query(User).filter(
                User.username == "editeduser"
            ).first()
            assert user.name == "Edited User"  # type: ignore
            assert user.username == "editeduser"  # type: ignore
            assert user.email == "editeduser@example.com"  # type: ignore
            assert user.phone_number == "+12123451234"  # type: ignore

        response = await Login(
            username = "editeduser",
            password = "password456"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert response.status_code == 200
        assert response.message == None
        assert response.fields is not None
        assert "jwt" in response.fields
        assert "not_before" in response.fields
        assert "expires_at" in response.fields

        assert isinstance(response.fields["jwt"], str)
        assert response.fields["not_before"] == None
        assert response.fields["expires_at"] == None

    def test_edit_user(self) -> None:
        run(self.__test_edit_user())

    async def __test_edit_name(self) -> None:
        response = await Register(
            name = "Test User",
            username = "testuser_name",
            email = "testuser_name@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        response = await Edit(
            jwt = jwt,
            name = "Updated Name"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User updated successfully"
        assert response.fields == None

        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_name"
            ).first()
            assert user.name == "Updated Name"  # type: ignore
            assert user.username == "testuser_name"  # type: ignore
            assert user.email == "testuser_name@example.com"  # type: ignore
            assert user.phone_number == "+12125551234"  # type: ignore

    def test_edit_name(self) -> None:
        run(self.__test_edit_name())

    async def __test_edit_username(self) -> None:
        response = await Register(
            name = "Test User",
            username = "testuser_username",
            email = "testuser_username@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        response = await Edit(
            jwt = jwt,
            username = "updateduser"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User updated successfully"
        assert response.fields == None

        with database.session() as session:
            user = session.query(User).filter(
                User.username == "updateduser"
            ).first()
            assert user.name == "Test User"  # type: ignore
            assert user.username == "updateduser"  # type: ignore
            assert user.email == "testuser_username@example.com"  # type: ignore
            assert user.phone_number == "+12125551234"  # type: ignore

        # Test login with new username
        response = await Login(
            username = "updateduser",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert response.status_code == 200
        assert response.message == None
        assert response.fields is not None
        assert "jwt" in response.fields

    def test_edit_username(self) -> None:
        run(self.__test_edit_username())

    async def __test_edit_email(self) -> None:
        response = await Register(
            name = "Test User",
            username = "testuser_email",
            email = "testuser_email@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        response = await Edit(
            jwt = jwt,
            email = "updated@example.com"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User updated successfully"
        assert response.fields == None

        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_email"
            ).first()
            assert user.name == "Test User"  # type: ignore
            assert user.username == "testuser_email"  # type: ignore
            assert user.email == "updated@example.com"  # type: ignore
            assert user.phone_number == "+12125551234"  # type: ignore

    def test_edit_email(self) -> None:
        run(self.__test_edit_email())

    async def __test_edit_phone_number(self) -> None:
        response = await Register(
            name = "Test User",
            username = "testuser_phone",
            email = "testuser_phone@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        response = await Edit(
            jwt = jwt,
            phone_number = "+12129999999"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User updated successfully"
        assert response.fields == None

        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_phone"
            ).first()
            assert user.name == "Test User"  # type: ignore
            assert user.username == "testuser_phone"  # type: ignore
            assert user.email == "testuser_phone@example.com"  # type: ignore
            assert user.phone_number == "+12129999999"  # type: ignore

    def test_edit_phone_number(self) -> None:
        run(self.__test_edit_phone_number())

    async def __test_edit_password(self) -> None:
        response = await Register(
            name = "Test User",
            username = "testuser_password",
            email = "testuser_password@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        fields = cast(Dict[str, Any], response.fields)
        jwt = fields["jwt"]

        response = await Edit(
            jwt = jwt,
            password = "newpassword123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert response.status_code == 200
        assert response.message == "User updated successfully"
        assert response.fields == None

        with database.session() as session:
            user = session.query(User).filter(
                User.username == "testuser_password"
            ).first()
            assert user.name == "Test User"  # type: ignore
            assert user.username == "testuser_password"  # type: ignore
            assert user.email == "testuser_password@example.com"  # type: ignore
            assert user.phone_number == "+12125551234"  # type: ignore

        # Test login with new password
        response = await Login(
            username = "testuser_password",
            password = "newpassword123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert response.status_code == 200
        assert response.message == None
        assert response.fields is not None
        assert "jwt" in response.fields

    def test_edit_password(self) -> None:
        run(self.__test_edit_password())


if __name__ == "__main__":
    main()
