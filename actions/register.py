from typing import TYPE_CHECKING, override

from pydantic import Field, constr, EmailStr, field_validator, model_validator
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

class Register(ActionRunner):
    username: constr(
        min_length = getenv("MIN_USERNAME_LENGTH"),
        max_length = getenv("MAX_USERNAME_LENGTH")
    ) = Field(
        description = "The username"
    )

    name: constr(
        min_length = 1,
        max_length = 255
    ) = Field(
        description = "The user's full name"
    )

    email: EmailStr = Field(
        description = "The user's email address"
    )

    phone_number: str = Field(
        description = "The user's phone number in any format (will be converted to E.164)"
    )

    password: constr(
        min_length = getenv("MIN_PASSWORD_LENGTH"),
        max_length = getenv("MAX_PASSWORD_LENGTH")
    ) = Field(
        description = "The password"
    )

    not_before: Union[int, None] = Field(
        description = "Sets the JWT not before date in unix timestamp",
        default = None
    )
    
    expire_at: Union[int, None] = Field(
        description = "Sets the JWT expiration date in unix timestamp",
        default = None
    )

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """
        Validate and format phone number to E.164 standard.
        
        Parameters:
            v (str): The phone number in any format.
            
        Returns:
            str: The phone number in E.164 format.
            
        Raises:
            ValueError: If the phone number is invalid.
        """
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

    @model_validator(mode = 'after')
    def validate_not_before_before_expire_at(self) -> 'Register':
        """
        Validate that not_before is before expire_at if both are provided.
        
        Returns:
            Register: The validated instance.
            
        Raises:
            ValueError: If not_before is after expire_at.
        """
        if self.not_before is not None and self.expire_at is not None and self.not_before > self.expire_at:
            raise ValueError("Not before date must be before expiration date")
        return self

    @classmethod
    @override
    def description(cls) -> str:
        return "Creates a new user and returns the associated jwt token"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        
        # insert user
        try:
            with database.transaction() as db:
                user = User(
                    username = self.username,
                    name = self.name,
                    email = self.email,
                    phone_number = self.phone_number,
                    password_digest = hashpw(
                        self.password.encode("utf-8"),
                        gensalt()
                    ).decode("utf-8")
                )
                db.add(user)
                db.flush()  # assign id without ending txn
                user_id = user.id
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
            "iat": datetime.now(UTC).timestamp(),
        }
        if self.not_before is not None:
            claims["nbf"] = int(self.not_before)
        if self.expire_at is not None:
            claims["exp"] = int(self.expire_at)

        return ActionResponse(
            status_code = 201,
            fields = {
                "jwt": encode(
                    claims,
                    secret,
                    algorithm = getenv("JWT_ALGORITHM")
                ),
                "expires_at": self.expire_at,
            },
        )