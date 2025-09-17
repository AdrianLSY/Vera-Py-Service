from datetime import UTC, datetime
from os import getenv
from typing import TYPE_CHECKING, Any, Dict, Union, override
from uuid import uuid4

import phonenumbers
from bcrypt import checkpw
from jwt import encode  # type: ignore
from phonenumbers import NumberParseException
from pydantic import EmailStr, Field, constr, field_validator, model_validator
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.database import database
from models.user import User

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

def __get_env_int(var_name: str, default: int) -> int:
    """Get environment variable as int or return default."""
    value = getenv(var_name)
    return int(value) if value is not None else default

class Login(ActionRunner):
    username: Union[str, None] = Field(
        description = "The username",
        default = None,
        min_length = __get_env_int("MIN_USERNAME_LENGTH", 3),
        max_length = __get_env_int("MAX_USERNAME_LENGTH", 50)
    )

    email: Union[EmailStr, None] = Field(
        description = "The email address",
        default = None
    )

    password: str = Field(
        description = "The password",
        min_length = __get_env_int("MIN_PASSWORD_LENGTH", 8),
        max_length = __get_env_int("MAX_PASSWORD_LENGTH", 128)
    )

    not_before: Union[int, None] = Field(
        description = "The JWT not before date in unix timestamp",
        default = None
    )

    expires_at: Union[int, None] = Field(
        description = "The JWT expiration date in unix timestamp",
        default = None
    )

    @classmethod
    @override
    def description(cls) -> str:
        return "Generates a JWT token for an existing user"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:

        # validate that exactly one identifier is provided
        identifier_count = sum([
            self.username is not None,
            self.email is not None,
        ])

        if identifier_count == 0:
            return ActionResponse(
                status_code = 400,
                message = "Exactly one identifier (username, email, or phone_number) must be provided"
            )

        if identifier_count > 1:
            return ActionResponse(
                status_code = 400,
                message = "Only one identifier (username, email, or phone_number) can be provided"
            )

        # lookup user and verify password
        try:
            with database.transaction() as db:
                # Find user by the provided identifier
                if self.username is not None:
                    user = db.query(User).filter(
                        User.username == self.username,
                        User.deleted_at.is_(None)
                    ).first()
                else:
                    user = db.query(User).filter(
                        User.email == self.email,
                        User.deleted_at.is_(None)
                    ).first()

                if user is None:
                    return ActionResponse(
                        status_code = 404,
                        message = "User not found"
                    )

                # verify password
                if not checkpw(
                    self.password.encode("utf-8"),
                    user.password_digest.encode("utf-8")
                ):
                    return ActionResponse(
                        status_code = 401,
                        message = "Invalid password"
                    )

                user_id = user.id

        except Exception as e:
            return ActionResponse(
                status_code = 500,
                message = f"Database error: {str(e)}",
            )

        # build the JWT
        secret = getenv("JWT_SECRET")
        if not secret:
            return ActionResponse(
                status_code = 500,
                message = "Missing JWT secret"
            )

        claims: Dict[str, Any] = {
            "jti": str(uuid4()),
            "iss": getenv("JWT_ISSUER"),
            "aud": getenv("JWT_AUDIENCE"),
            "sub": str(user_id),
            "iat": datetime.now(UTC).timestamp(),
        }
        if self.not_before is not None:
            claims["nbf"] = int(self.not_before)
        if self.expires_at is not None:
            claims["exp"] = int(self.expires_at)

        return ActionResponse(
            status_code = 200,
            fields = {
                "jwt": encode(
                    claims,
                    secret,
                    algorithm = getenv("JWT_ALGORITHM")
                ),
                "expires_at": self.expires_at,
            },
        )
