from unittest import expectedFailure
from unittest import TestCase, main
from os import environ, getenv
from core.database import Database
from actions.register import Register
from unittest.mock import MagicMock
from asyncio import run
from time import time
from jwt import decode

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
        self.db.migrate()
        self.jwt_secret = getenv("JWT_SECRET")

        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is not set")

    def tearDown(self) -> None:
        """
        Clean up after each test method.
        """
        # Restore original environment
        environ.clear()
        environ.update(self.original_env)
        self.db.teardown()
        pass

    def __verify_jwt(self, jwt: str, expected_claims: dict) -> None:
        """
        Verify the JWT token.
        """
        claims = decode(
            jwt,
            self.jwt_secret,
            algorithms = [getenv("JWT_ALGORITHM", "HS256")],
            audience = getenv("JWT_AUDIENCE"),
            issuer = getenv("JWT_ISSUER")
        )
        assert claims == expected_claims

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

    def test_register_phone_only(self) -> None:
        """
        Test register action with phone number only.
        """
        run(self.__test_register_phone_only())

    async def __test_register_with_timestamps(self) -> None:
        """
        Test register action with not_before and expires_at timestamps.
        """
        current_time = int(time())
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
        current_time = int(time())
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

    def test_register_invalid_timestamps(self) -> None:
        """
        Test register action with invalid timestamps.
        """
        run(self.__test_register_invalid_timestamps())

    async def __test_register_only_not_before(self) -> None:
        """
        Test register action with only not_before timestamp.
        """
        current_time = int(time())
        not_before_time = current_time + 60  # 1 minute from now

        result = await Register(
            username = "onlynotbefore",
            name = "Only Not Before User",
            email = None,
            password = "password123",
            not_before = not_before_time,
            expires_at = None
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert result.status_code == 201
        assert isinstance(result.fields, dict)
        assert "jwt" in result.fields
        assert result.fields["not_before"] == not_before_time
        assert result.fields["expires_at"] == None

    def test_register_only_not_before(self) -> None:
        """
        Test register action with only not_before timestamp.
        """
        run(self.__test_register_only_not_before())

    async def __test_register_only_expires_at(self) -> None:
        """
        Test register action with only expires_at timestamp.
        """
        current_time = int(time())
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

    def test_register_only_expires_at(self) -> None:
        """
        Test register action with only expires_at timestamp.
        """
        run(self.__test_register_only_expires_at())

if __name__ == '__main__':
    main()
