from asyncio import run
from os import environ, getenv
from typing import Any, Dict, cast
from unittest import TestCase, main
from unittest.mock import MagicMock
from uuid import UUID

from jwt import decode  # type: ignore

from actions.login import Login
from actions.logout import Logout
from actions.register import Register
from core.database import Database
from models.revocation import Revocation


class TestLogout(TestCase):
    """
    Integration test cases for the Database class using real database.
    """
    original_env: Dict[str, str]  # type: ignore
    magic_mock: MagicMock  # type: ignore
    db: Database  # type: ignore
    jwt_secret: str  # type: ignore
    register_jwt: str  # type: ignore
    register_claims: Dict[str, Any]  # type: ignore
    login_jwt: str  # type: ignore
    login_claims: Dict[str, Any]  # type: ignore

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

        register_response = run(self.__register_user())
        login_response = run(self.__login_user())

        # Type assertions for fields access
        assert isinstance(register_response.fields, dict)  # type: ignore
        assert isinstance(login_response.fields, dict)  # type: ignore

        register_fields = cast(Dict[str, Any], register_response.fields)
        login_fields = cast(Dict[str, Any], login_response.fields)

        self.register_jwt = register_fields["jwt"]
        self.register_claims = self.decode_jwt(self.register_jwt)

        self.login_jwt = login_fields["jwt"]
        self.login_claims = self.decode_jwt(self.login_jwt)

    def tearDown(self) -> None:  # type: ignore
        """
        Clean up after each test method.
        """
        # Restore original environment
        environ.clear()
        environ.update(self.original_env)
        self.db.teardown()
        pass

    async def __register_user(self) -> None:
        return await Register(
            name = "Test User",
            username = "testuser",
            email = "testuser@example.com",
            phone_number = "+12125551234",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

    async def __login_user(self) -> None:
        return await Login(
            username = "testuser",
            password = "password123"
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

    def decode_jwt(self, jwt: str) -> Dict[str, Any]:
        return decode(
            jwt,
            self.jwt_secret,
            algorithms = [getenv("JWT_ALGORITHM", "HS256")],
            audience = getenv("JWT_AUDIENCE"),
            issuer = getenv("JWT_ISSUER")
        )

    async def __test_logout(self) -> None:
        await Logout(
            jwt = self.register_jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )
        await Logout(
            jwt = self.login_jwt
        ).run(
            client = self.magic_mock,
            websocket = self.magic_mock
        )

        with self.db.session() as session:
            revocations = session.query(Revocation).all()
            assert len(revocations) == 2

            # Check that both JTIs are in the revocations
            revocation_jtis = {rev.jti for rev in revocations}
            assert UUID(self.register_claims["jti"]) in revocation_jtis
            assert UUID(self.login_claims["jti"]) in revocation_jtis

    def test_logout(self) -> None:
        run(self.__test_logout())


if __name__ == "__main__":
    main()
