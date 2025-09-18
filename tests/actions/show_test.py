from asyncio import run
from datetime import UTC, datetime
from os import environ, getenv
from typing import Any, Dict, cast
from unittest import TestCase, main
from unittest.mock import MagicMock

from jwt import decode  # type: ignore

from actions.register import Register
from actions.show import Show
from core.database import database


class ShowTest(TestCase):
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

    def __verify_jwt(self, jwt: str) -> Dict[str, Any]:
        """
        Verify the JWT token.

        Parameters:
            jwt (str): The JWT token to verify.

        Returns:
            Dict[str, Any]: The decoded claims from the JWT.
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

    async def __test_show_valid_jwt(self) -> None:
        """
        Test show action with a valid JWT token.
        """
        # First register a user to get a valid JWT
        register_response = await Register(
            name = "Test User",
            username = "testuser",
            email = "testuser@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert register_response.status_code == 201
        assert register_response.fields is not None
        assert "jwt" in register_response.fields

        fields = cast(Dict[str, Any], register_response.fields)
        jwt = fields["jwt"]
        self.__verify_jwt(jwt = jwt)

        # Now test the show action with the valid JWT
        show_response = await Show(
            jwt = jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert show_response.status_code == 200
        assert show_response.message is None
        assert show_response.fields is not None
        assert "user" in show_response.fields
        assert "claims" in show_response.fields

        response_fields = cast(Dict[str, Any], show_response.fields)
        user_data = cast(Dict[str, Any], response_fields["user"])
        assert user_data["username"] == "testuser"
        assert "id" in user_data
        assert "created_at" in user_data
        assert "updated_at" in user_data

        claims_data = cast(Dict[str, Any], response_fields["claims"])
        assert claims_data["sub"] == str(user_data["id"])

    def test_show_valid_jwt(self) -> None:
        """
        Test show action with valid JWT.
        """
        run(self.__test_show_valid_jwt())

    async def __test_show_invalid_jwt_malformed(self) -> None:
        """
        Test show action with malformed JWT token.
        """
        show_response = await Show(
            jwt = "invalid.jwt.token"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert show_response.status_code == 401
        assert "Invalid token" in show_response.message
        assert show_response.fields is None

    def test_show_invalid_jwt_malformed(self) -> None:
        """
        Test show action with malformed JWT.
        """
        run(self.__test_show_invalid_jwt_malformed())

    async def __test_show_invalid_jwt_wrong_secret(self) -> None:
        """
        Test show action with JWT signed with wrong secret.
        """
        from jwt import encode  # type: ignore

        # Create a JWT with wrong secret
        wrong_claims: Dict[str, Any] = {
            "jti": "test-jti",
            "iss": getenv("JWT_ISSUER"),
            "aud": getenv("JWT_AUDIENCE"),
            "sub": "test-user-id",
            "iat": int(datetime.now(UTC).timestamp())
        }

        wrong_jwt = encode(
            wrong_claims,
            "wrong-secret",
            algorithm = getenv("JWT_ALGORITHM", "HS256")
        )

        show_response = await Show(
            jwt = wrong_jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert show_response.status_code == 401
        assert "Invalid token" in show_response.message
        assert show_response.fields is None

    def test_show_invalid_jwt_wrong_secret(self) -> None:
        """
        Test show action with JWT signed with wrong secret.
        """
        run(self.__test_show_invalid_jwt_wrong_secret())

    async def __test_show_invalid_jwt_missing_claims(self) -> None:
        """
        Test show action with JWT missing required claims.
        """
        from jwt import encode  # type: ignore

        # Create a JWT missing required claims
        incomplete_claims: Dict[str, Any] = {
            "iss": getenv("JWT_ISSUER"),
            "aud": getenv("JWT_AUDIENCE"),
            "iat": int(datetime.now(UTC).timestamp())
            # Missing jti and sub
        }

        incomplete_jwt = encode(
            incomplete_claims,
            self.jwt_secret,
            algorithm = getenv("JWT_ALGORITHM", "HS256")
        )

        show_response = await Show(
            jwt = incomplete_jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert show_response.status_code == 401
        assert "Invalid token: missing required claims" in show_response.message
        assert show_response.fields is None

    def test_show_invalid_jwt_missing_claims(self) -> None:
        """
        Test show action with JWT missing required claims.
        """
        run(self.__test_show_invalid_jwt_missing_claims())

    async def __test_show_revoked_jwt(self) -> None:
        """
        Test show action with revoked JWT token.
        """
        from actions.logout import Logout

        # First register a user to get a valid JWT
        register_response = await Register(
            name = "Test User",
            username = "testuser_revoked",
            email = "testuser_revoked@example.com",
            phone_number = "+12125551235",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert register_response.status_code == 201
        assert register_response.fields is not None
        assert "jwt" in register_response.fields

        fields = cast(Dict[str, Any], register_response.fields)
        jwt = fields["jwt"]

        # Revoke the JWT
        logout_response = await Logout(
            jwt = jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert logout_response.status_code == 200

        # Now test the show action with the revoked JWT
        show_response = await Show(
            jwt = jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert show_response.status_code == 401
        assert "Token has been revoked" in show_response.message
        assert show_response.fields is None

    def test_show_revoked_jwt(self) -> None:
        """
        Test show action with revoked JWT.
        """
        run(self.__test_show_revoked_jwt())

    async def __test_show_nonexistent_user(self) -> None:
        """
        Test show action with JWT for non-existent user.
        """
        from uuid import uuid4

        from jwt import encode  # type: ignore

        # Create a JWT for a non-existent user
        fake_claims: Dict[str, Any] = {
            "jti": str(uuid4()),
            "iss": getenv("JWT_ISSUER"),
            "aud": getenv("JWT_AUDIENCE"),
            "sub": "999999",  # Non-existent user ID
            "iat": int(datetime.now(UTC).timestamp())
        }

        fake_jwt = encode(
            fake_claims,
            self.jwt_secret,
            algorithm = getenv("JWT_ALGORITHM", "HS256")
        )

        show_response = await Show(
            jwt = fake_jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        assert show_response.status_code == 404
        assert "User not found" in show_response.message
        assert show_response.fields is None

    def test_show_nonexistent_user(self) -> None:
        """
        Test show action with JWT for non-existent user.
        """
        run(self.__test_show_nonexistent_user())


if __name__ == "__main__":
    main()
