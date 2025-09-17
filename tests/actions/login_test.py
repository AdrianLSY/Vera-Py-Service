from asyncio import run
from datetime import UTC, datetime
from os import environ, getenv
from typing import Any, Dict
from unittest import TestCase, main
from unittest.mock import MagicMock

from jwt import decode  # type: ignore

from actions.login import Login
from actions.register import Register
from core.database import database


class TestLogin(TestCase):
    """
    Integration test cases for the Database class using real database.
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

        run(self.__register_user())

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

    async def __register_user(self) -> None:
        await Register(
            name = "Test User",
            username = "testuser",
            email = "testuser@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

    def __verify_jwt(self, jwt: str) -> Dict[str, Any]:
        """
        Verify the JWT token.
        """
        claims: Dict[str, Any] = decode(
            jwt,
            self.jwt_secret,
            algorithms = [getenv("JWT_ALGORITHM", "HS256")],
            audience = getenv("JWT_AUDIENCE"),
            issuer = getenv("JWT_ISSUER")
        )
        assert isinstance(claims, dict)
        assert "jti" in claims
        assert "iss" in claims
        assert "aud" in claims
        assert "sub" in claims
        assert "iat" in claims

        assert isinstance(claims["jti"], str)
        assert isinstance(claims["iss"], str)
        assert isinstance(claims["aud"], str)
        assert isinstance(claims["sub"], str)
        assert isinstance(claims["iat"], int)

        if "nbf" in claims:
            assert isinstance(claims["nbf"], int)
            assert claims["nbf"] <= claims["iat"]
        if "exp" in claims:
            assert isinstance(claims["exp"], int)
            assert claims["iat"] <= claims["exp"]
        if "nbf" in claims and "exp" in claims:
            assert claims["nbf"] <= claims["exp"]

        return claims

    async def __test_login_username(self) -> None:
        """
        Test register action with a username.
        """
        result = await Login(
            username = "testuser",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 200
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert "expires_at" in result.fields
        assert result.fields["expires_at"] == None

        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_login_username(self) -> None:
        """
        Test register action.
        """
        run(self.__test_login_username())

    async def __test_login_email(self) -> None:
        """
        Test register action with an email.
        """
        result = await Login(
            email = "testuser@example.com",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 200
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert "expires_at" in result.fields
        assert result.fields["expires_at"] == None

        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_login_email(self) -> None:
        """
        Test register action.
        """
        run(self.__test_login_email())

    async def __test_login_with_not_before(self) -> None:
        """
        Test login action with not_before timestamp.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())
        not_before_time = current_time - 1

        result = await Login(
            username = "testuser",
            password = "password123",
            not_before = not_before_time,
            expires_at = None
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 200
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert "not_before" in result.fields
        assert "expires_at" in result.fields
        assert result.fields["not_before"] == not_before_time
        assert result.fields["expires_at"] == None
        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_login_with_not_before(self) -> None:
        """
        Test login action with not_before timestamp.
        """
        run(self.__test_login_with_not_before())

    async def __test_login_with_expires_at(self) -> None:
        """
        Test login action with expires_at timestamp.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())
        expires_at_time = current_time + 3600

        result = await Login(
            username = "testuser",
            password = "password123",
            not_before = None,
            expires_at = expires_at_time
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 200
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert "not_before" in result.fields
        assert "expires_at" in result.fields
        assert result.fields["not_before"] == None
        assert result.fields["expires_at"] == expires_at_time
        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_login_with_expires_at(self) -> None:
        """
        Test login action with expires_at timestamp.
        """
        run(self.__test_login_with_expires_at())

    async def __test_login_with_both_timestamps(self) -> None:
        """
        Test login action with both not_before and expires_at timestamps.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())
        not_before_time = current_time - 1
        expires_at_time = current_time + 3600

        result = await Login(
            username = "testuser",
            password = "password123",
            not_before = not_before_time,
            expires_at = expires_at_time
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 200
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert "not_before" in result.fields
        assert "expires_at" in result.fields
        assert result.fields["not_before"] == not_before_time
        assert result.fields["expires_at"] == expires_at_time
        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_login_with_both_timestamps(self) -> None:
        """
        Test login action with both timestamps.
        """
        run(self.__test_login_with_both_timestamps())

    async def __test_login_invalid_timestamps(self) -> None:
        """
        Test login action with invalid timestamp combinations (not_before > expires_at).
        """
        current_time = int(datetime.now(tz = UTC).timestamp())
        not_before_time = current_time - 1
        expires_at_time = current_time - 60

        result = await Login(
            username = "testuser",
            password = "password123",
            not_before = not_before_time,
            expires_at = expires_at_time
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 400
        assert result.message == "Not before date must be before expiration date"
        assert result.fields == None

    def test_login_invalid_timestamps(self) -> None:
        """
        Test login action with invalid timestamps.
        """
        run(self.__test_login_invalid_timestamps())

    async def __test_login_only_not_before(self) -> None:
        """
        Test login action with only not_before timestamp.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())

        result = await Login(
            username = "testuser",
            password = "password123",
            not_before = current_time,
            expires_at = None
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert result.status_code == 200
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert "not_before" in result.fields
        assert "expires_at" in result.fields
        assert result.fields["not_before"] == current_time
        assert result.fields["expires_at"] == None
        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_login_only_not_before(self) -> None:
        """
        Test login action with only not_before timestamp.
        """
        run(self.__test_login_only_not_before())

    async def __test_login_only_expires_at(self) -> None:
        """
        Test login action with only expires_at timestamp.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())
        expires_at_time = current_time + 3600

        result = await Login(
            username = "testuser",
            password = "password123",
            not_before = None,
            expires_at = expires_at_time
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert result.status_code == 200
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert "not_before" in result.fields
        assert "expires_at" in result.fields
        assert result.fields["not_before"] == None
        assert result.fields["expires_at"] == expires_at_time
        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_login_only_expires_at(self) -> None:
        """
        Test login action with only expires_at timestamp.
        """
        run(self.__test_login_only_expires_at())


if __name__ == "__main__":
    main()
