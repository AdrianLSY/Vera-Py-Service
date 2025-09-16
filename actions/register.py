from typing import TYPE_CHECKING, override, Annotated

from pydantic import Field, EmailStr
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.database import database
from bcrypt import hashpw, gensalt
from os import getenv
from uuid import uuid4
from jwt import encode
from sqlalchemy.exc import IntegrityError
from models.user import User
from datetime import datetime, UTC
from typing import Union
import phonenumbers
from phonenumbers import NumberParseException


if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

def __get_required_env_int(var_name: str) -> int:
    """
    Get required integer environment variable or raise error.

    Parameters:
        var_name (str): The name of the environment variable to retrieve.

    Returns:
        int: The value of the environment variable as an integer.

    Raises:
        RuntimeError: If the environment variable is not set.
    """
    value = getenv(var_name)
    if value is None:
        raise RuntimeError(f"Required environment variable {var_name} is not set")
    return int(value)

MIN_NAME_LENGTH = __get_required_env_int("MIN_NAME_LENGTH")
MAX_NAME_LENGTH = __get_required_env_int("MAX_NAME_LENGTH")
MIN_USERNAME_LENGTH = __get_required_env_int("MIN_USERNAME_LENGTH")
MAX_USERNAME_LENGTH = __get_required_env_int("MAX_USERNAME_LENGTH")
MIN_EMAIL_LENGTH = __get_required_env_int("MIN_EMAIL_LENGTH")
MAX_EMAIL_LENGTH = __get_required_env_int("MAX_EMAIL_LENGTH")
MIN_PASSWORD_LENGTH = __get_required_env_int("MIN_PASSWORD_LENGTH")
MAX_PASSWORD_LENGTH = __get_required_env_int("MAX_PASSWORD_LENGTH")

class Register(ActionRunner):
    name: Annotated[str, Field(
        min_length = MIN_NAME_LENGTH,
        max_length = MAX_NAME_LENGTH,
        description = "The user's name"
    )]

    username: Annotated[Union[str, None], Field(
        min_length = MIN_USERNAME_LENGTH,
        max_length = MAX_USERNAME_LENGTH,
        description = "The username",
        default = None
    )]

    email: Annotated[Union[EmailStr, None], Field(
        min_length = MIN_EMAIL_LENGTH,
        max_length = MAX_EMAIL_LENGTH,
        description = "The user's email address",
        default = None
    )]

    phone_number: Union[str, None] = Field(
        description = "The user's phone number in any format (will be converted to E.164)",
        default = None
    )

    password: Annotated[str, Field(
        min_length = MIN_PASSWORD_LENGTH,
        max_length = MAX_PASSWORD_LENGTH,
        description = "The password"
    )]

    not_before: Union[int, None] = Field(
        description = "Sets the JWT not before date in unix timestamp",
        default = None
    )

    expires_at: Union[int, None] = Field(
        description = "Sets the JWT expiration date in unix timestamp",
        default = None
    )

    @classmethod
    @override
    def description(cls) -> str:
        return "Creates a new user and returns the associated jwt token"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        # Validate at least one identifier is provided (username or email only)
        if not any([self.username, self.email]):
            return ActionResponse(
                status_code = 400,
                message = "At least one of username or email must be provided"
            )

        # Validate not_before is before expires_at
        if self.not_before is not None and self.expires_at is not None and self.not_before > self.expires_at:
            return ActionResponse(
                status_code = 400,
                message = "Not before date must be before expiration date"
            )

        # Validate expires_at is not before the current time
        if self.expires_at is not None and self.expires_at < datetime.now(tz = UTC).timestamp():
            return ActionResponse(
                status_code = 400,
                message = "Expiration date must be in the future"
            )

        # Validate and format phone number if provided
        formatted_phone_number = None
        if self.phone_number is not None:
            try:
                # Parse the phone number
                parsed_number = phonenumbers.parse(self.phone_number, None)

                # Check if it's a valid number
                if not phonenumbers.is_valid_number(parsed_number):
                    return ActionResponse(
                        status_code = 400,
                        message = "Invalid phone number"
                    )

                # Format to E.164
                formatted_phone_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

            except NumberParseException as e:
                return ActionResponse(
                    status_code = 400,
                    message = f"Invalid phone number format: {str(e)}"
                )

        try:
            with database.transaction() as db:
                user_data = {
                    "name": self.name,
                    "password_digest": hashpw(
                        self.password.encode("utf-8"),
                        gensalt()
                    ).decode("utf-8")
                }

                # Only set fields that are not None
                if self.username is not None:
                    user_data["username"] = self.username
                if self.email is not None:
                    user_data["email"] = self.email
                if formatted_phone_number is not None:
                    user_data["phone_number"] = formatted_phone_number

                user = User(**user_data)
                db.add(user)
                db.flush()  # assign id without ending txn
                user_id = user.id
        except IntegrityError:
            return ActionResponse(
                status_code = 409,
                message = "User already exists"
            )
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

        claims = {
            "jti": str(uuid4()),
            "iss": getenv("JWT_ISSUER"),
            "aud": getenv("JWT_AUDIENCE"),
            "sub": str(user_id),
            "iat": int(datetime.now(UTC).timestamp())
        }
        if self.not_before is not None:
            claims["nbf"] = int(self.not_before)
        if self.expires_at is not None:
            claims["exp"] = int(self.expires_at)

        return ActionResponse(
            status_code = 201,
            fields = {
                "jwt": encode(
                    claims,
                    secret,
                    algorithm = getenv("JWT_ALGORITHM")
                ),
                "not_before": self.not_before,
                "expires_at": self.expires_at
            },
        )
