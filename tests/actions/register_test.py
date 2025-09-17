from asyncio import run
from datetime import UTC, datetime
from os import environ, getenv
from typing import Any, Dict
from unittest import TestCase, expectedFailure, main
from unittest.mock import MagicMock

from jwt import decode  # type: ignore

from actions.register import Register
from core.database import Database


class TestRegister(TestCase):
    """
    Integration test cases for the Database class using real database.
    """
    original_env: Dict[str, str]  # type: ignore
    magic_mock: MagicMock  # type: ignore
    db: Database  # type: ignore
    jwt_secret: str  # type: ignore

    def setUp(self) -> None:  # type: ignore
        """
        Set up test fixtures before each test method.
        """
        # Set up test environment variables
        self.original_env = environ.copy()
        environ.update({"ENVIRONMENT": "test"})

        self.magic_mock = MagicMock()
        self.db = Database()
        self.db.initialize()
        self.db.migrate()
        self.jwt_secret = getenv("JWT_SECRET")

        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is not set")

    def tearDown(self) -> None:  # type: ignore
        """
        Clean up after each test method.
        """
        # Restore original environment
        environ.clear()
        environ.update(self.original_env)
        self.db.teardown()
        pass

    def __verify_jwt(self, jwt: str) -> None:
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

    async def __test_register_username(self) -> None:
        """
        Test register action with a username.
        """
        result = await Register(
            username = "testuser",
            name = "Test User",
            email = None,
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 201
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert result.fields["not_before"] == None
        assert result.fields["expires_at"] == None

        result = await Register(
            username = "testuser",
            name = "Test User",
            email = None,
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 409
        assert result.message == "User already exists"
        assert result.fields is None

    def test_register_username(self) -> None:
        """
        Test register action.
        """
        run(self.__test_register_username())

    async def __test_register_email(self) -> None:
        """
        Test register action with a username.
        """
        # First user
        result = await Register(
            username = None,
            name = "Test User",
            email = "testuser@example.com",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 201
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert result.fields["not_before"] == None
        assert result.fields["expires_at"] == None
        self.__verify_jwt(jwt = result.fields["jwt"])

        # Second user
        result = await Register(
            username = None,
            name = "Test User",
            email = "testuser@example.com",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 409
        assert result.message == "User already exists"
        assert result.fields is None

    def test_register_email(self) -> None:
        """
        Test register action.
        """
        run(self.__test_register_email())

    async def __test_register_with_phone_number(self) -> None:
        """
        Test register action with username and phone number.
        """
        # Test with valid username and phone number
        # First user
        result = await Register(
            username = "phoneuser",
            name = "Test User",
            email = None,
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 201
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert result.fields["not_before"] == None
        assert result.fields["expires_at"] == None
        self.__verify_jwt(jwt = result.fields["jwt"])

        # Second user
        result = await Register(
            username = "phoneuser",
            name = "Test User",
            email = None,
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 409
        assert result.message == "User already exists"
        assert result.fields is None

    def test_register_with_phone_number(self) -> None:
        """
        Test register action with username and phone number.
        """
        run(self.__test_register_with_phone_number())

    async def __test_register_phone_number_invalid(self) -> None:
        """
        Test register action with invalid phone numbers.
        """
        # Test with invalid phone number but valid username
        result = await Register(
            username = "testuser",
            name = "Test User",
            email = None,
            phone_number = "invalid-phone",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 400
        assert result.message == "Invalid phone number format: (1) The string supplied did not seem to be a phone number."
        assert result.fields == None

        # Test with incomplete phone number but valid email
        result = await Register(
            username = None,
            name = "Test User",
            email = "test@example.com",
            phone_number = "123",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 400
        assert result.message == "Invalid phone number format: (0) Missing or invalid default region."
        assert result.fields == None

    def test_register_phone_number_invalid(self) -> None:
        """
        Test register action with invalid phone numbers.
        """
        run(self.__test_register_phone_number_invalid())

    async def __test_register_no_identifier(self) -> None:
        """
        Test register action without username or email (phone number only is not sufficient).
        """
        result = await Register(
            username = None,
            name = "Test User",
            email = None,
            phone_number = None,
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 400
        assert result.message == "At least one of username or email must be provided"
        assert result.fields == None

    def test_register_no_identifier(self) -> None:
        """
        Test register action without username or email.
        """
        run(self.__test_register_no_identifier())

    async def __test_register_phone_only(self) -> None:
        """
        Test register action with only phone number (should fail).
        """
        result = await Register(
            username = None,
            name = "Test User",
            email = None,
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 400
        assert result.message == "At least one of username or email must be provided"
        assert result.fields == None

    def test_register_phone_only(self) -> None:
        """
        Test register action with phone number only.
        """
        run(self.__test_register_phone_only())

    async def __test_register_with_timestamps(self) -> None:
        """
        Test register action with not_before and expires_at timestamps.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())
        not_before_time = current_time + 60  # 1 minute from now
        expires_at_time = current_time + 3600  # 1 hour from now

        result = await Register(
            username = "timestampuser",
            name = "Timestamp User",
            email = None,
            password = "password123",
            not_before = not_before_time,
            expires_at = expires_at_time
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert result.status_code == 201
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert result.fields["not_before"] == not_before_time
        assert result.fields["expires_at"] == expires_at_time

    def test_register_with_timestamps(self) -> None:
        """
        Test register action with timestamps.
        """
        run(self.__test_register_with_timestamps())

    async def __test_register_invalid_timestamps(self) -> None:
        """
        Test register action with invalid timestamp combinations.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())
        not_before_time = current_time + 3600  # 1 hour from now
        expires_at_time = current_time + 60   # 1 minute from now (before not_before)

        result = await Register(
            username = "invalidtimestamp",
            name = "Invalid Timestamp User",
            email = None,
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

        result = await Register(
            username = "invalidtimestamp",
            name = "Invalid Timestamp User",
            email = None,
            password = "password123",
            expires_at = current_time - 100
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        assert result.status_code == 400
        assert result.message == "Expiration date must be in the future"
        assert result.fields == None

    def test_register_invalid_timestamps(self) -> None:
        """
        Test register action with invalid timestamps.
        """
        run(self.__test_register_invalid_timestamps())

    async def __test_register_only_not_before(self) -> None:
        """
        Test register action with only not_before timestamp.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())

        result = await Register(
            username = "onlynotbefore",
            name = "Only Not Before User",
            email = None,
            password = "password123",
            not_before = current_time,
            expires_at = None
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert result.status_code == 201
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert result.fields["not_before"] == current_time
        assert result.fields["expires_at"] == None
        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_register_only_not_before(self) -> None:
        """
        Test register action with only not_before timestamp.
        """
        run(self.__test_register_only_not_before())

    async def __test_register_only_expires_at(self) -> None:
        """
        Test register action with only expires_at timestamp.
        """
        current_time = int(datetime.now(tz = UTC).timestamp())
        expires_at_time = current_time + 3600  # 1 hour from now

        result = await Register(
            username = "onlyexpires",
            name = "Only Expires User",
            email = None,
            password = "password123",
            not_before = None,
            expires_at = expires_at_time
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert result.status_code == 201
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert result.fields["not_before"] == None
        assert result.fields["expires_at"] == expires_at_time
        self.__verify_jwt(jwt = result.fields["jwt"])

    def test_register_only_expires_at(self) -> None:
        """
        Test register action with only expires_at timestamp.
        """
        run(self.__test_register_only_expires_at())

if __name__ == '__main__':
    main()
