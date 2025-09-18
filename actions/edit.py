from os import getenv
from typing import TYPE_CHECKING, Any, Dict, Union, override

import phonenumbers
from bcrypt import gensalt, hashpw
from jwt import InvalidTokenError, decode  # type: ignore
from phonenumbers import NumberParseException
from pydantic import EmailStr, Field, constr, field_validator
from sqlalchemy.exc import IntegrityError
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.database import database
from models.revocation import Revocation
from models.user import User

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

def _get_env_int(var_name: str, default: int) -> int:
    """Get environment variable as int or return default."""
    value = getenv(var_name)
    return int(value) if value is not None else default

class Edit(ActionRunner):
    jwt: Union[str, None] = Field(
        description = "Optional JWT token to query the user. pass this or user_id,",
        default = None
    )

    user_id: Union[int, None] = Field(
        description = "Optional user ID to query the user. pass this or the jwt",
        default = None
    )

    username: Union[str, None] = Field(
        description = "The new username",
        default = None,
        min_length = _get_env_int("MIN_USERNAME_LENGTH", 3),
        max_length = _get_env_int("MAX_USERNAME_LENGTH", 50)
    )

    name: Union[str, None] = Field(
        description = "The new name",
        default = None,
        min_length = 1,
        max_length = 255
    )

    email: Union[EmailStr, None] = Field(
        description = "The new email address",
        default = None
    )

    phone_number: Union[str, None] = Field(
        description = "The new phone number in any format (will be converted to E.164)",
        default = None
    )

    password: Union[str, None] = Field(
        description = "The new password",
        default = None,
        min_length = _get_env_int("MIN_PASSWORD_LENGTH", 8),
        max_length = _get_env_int("MAX_PASSWORD_LENGTH", 128)
    )

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Union[str, None]) -> Union[str, None]:
        """
        Validate and format phone number to E.164 standard.

        Parameters:
            v (Union[str, None]): The phone number in any format, or None.

        Returns:
            Union[str, None]: The phone number in E.164 format, or None.

        Raises:
            ValueError: If the phone number is invalid.
        """
        if v is None:
            return None

        try:
            # Parse the phone number
            parsed_number = phonenumbers.parse(v, None)

            # Check if it's a valid number
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number")

            # Format to E.164
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

        except NumberParseException as e:
            raise ValueError(f"Invalid phone number format: {str(e)}")

    @classmethod
    @override
    def description(cls) -> str:
        return "Updates user username and/or password using JWT authentication"

    def __validate_jwt(self) -> Union[int, ActionResponse]:
        # decode and validate JWT
        secret = getenv("JWT_SECRET")
        if not secret:
            return ActionResponse(
                status_code = 500,
                message = "Missing JWT secret"
            )

        try:
            # decode JWT with validation
            claims: Dict[str, Any] = decode(
                self.jwt,
                secret,
                algorithms = [getenv("JWT_ALGORITHM", "HS256")],
                audience = getenv("JWT_AUDIENCE"),
                issuer = getenv("JWT_ISSUER")
            )

            jti = claims.get("jti")
            user_id = claims.get("sub")

            if not jti or not user_id:
                return ActionResponse(
                    status_code = 401,
                    message = "Invalid token: missing required claims"
                )

        except InvalidTokenError as e:
            return ActionResponse(
                status_code = 401,
                message = f"Invalid token: {str(e)}"
            )
        except Exception as e:
            return ActionResponse(
                status_code = 500,
                message = f"Token validation error: {str(e)}"
            )

        with database.transaction() as db:
            revoked = db.query(
                    Revocation
                ).filter(
                    Revocation.jti == jti
                ).first()

        if revoked:
            return ActionResponse(
                status_code = 401,
                message = "Token has been revoked"
            )

        return int(user_id)

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        user_id = self.user_id

        # validate if jwt or user_id is provided
        if self.jwt is None and self.user_id is None:
            return ActionResponse(
                status_code = 400,
                message = "Either JWT or user_id must be provided"
            )

        # validate that at least one field is provided
        if self.username is None and self.name is None and self.email is None and self.phone_number is None and self.password is None:
            return ActionResponse(
                status_code = 400,
                message = "At least one field (username, name, email, phone_number, or password) must be provided"
            )

        if self.jwt is not None:
            response = self.__validate_jwt()
            if isinstance(response, ActionResponse):
                return response

            jwt_user_id = response

            # If user_id is also provided, check consistency
            if user_id is not None and jwt_user_id != user_id:
                return ActionResponse(
                    status_code = 401,
                    message = "user id is not consistent between JWT and user_id"
                )

            user_id = jwt_user_id

        try:
            with database.transaction() as db:

                # get user
                user = db.query(User).filter(
                    User.id == user_id,
                    User.deleted_at.is_(None)
                ).first()

                if not user:
                    return ActionResponse(
                        status_code = 404,
                        message = "User not found"
                    )

                # update fields
                if self.username is not None:
                    user.username = self.username

                if self.name is not None:
                    user.name = self.name

                if self.email is not None:
                    user.email = self.email

                if self.phone_number is not None:
                    user.phone_number = self.phone_number

                if self.password is not None:
                    user.password_digest = hashpw(
                        self.password.encode("utf-8"),
                        gensalt()
                    ).decode("utf-8")

                db.flush()  # ensure changes are persisted

        except IntegrityError as e:
            # unique constraint violation
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "username" in error_msg.lower():
                return ActionResponse(
                    status_code = 409,
                    message = "Username already taken"
                )
            elif "email" in error_msg.lower():
                return ActionResponse(
                    status_code = 409,
                    message = "Email already registered"
                )
            elif "phone_number" in error_msg.lower():
                return ActionResponse(
                    status_code = 409,
                    message = "Phone number already registered"
                )
            else:
                return ActionResponse(
                    status_code = 409,
                    message = "User with this information already exists"
                )
        except Exception as e:
            return ActionResponse(
                status_code = 500,
                message = f"Database error: {str(e)}"
            )

        return ActionResponse(
            status_code = 200,
            message = "User updated successfully"
        )
