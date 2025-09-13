from typing import TYPE_CHECKING, override, Union

from pydantic import Field, constr, EmailStr, field_validator, model_validator
from websockets import ClientConnection
from bcrypt import checkpw
from os import getenv
from uuid import uuid4
from jwt import encode
from datetime import datetime, UTC

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.database import database
from models.user import User
import phonenumbers
from phonenumbers import NumberParseException

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Login(ActionRunner):
    username: Union[
        constr(
            min_length = getenv("MIN_USERNAME_LENGTH"),
            max_length = getenv("MAX_USERNAME_LENGTH")
        ),
        None
    ] = Field(
        description = "The username",
        default = None
    )

    email: Union[EmailStr, None] = Field(
        description = "The email address",
        default = None
    )

    phone_number: Union[str, None] = Field(
        description = "The phone number in any format (will be converted to E.164)",
        default = None
    )

    password: constr(
        min_length = getenv("MIN_PASSWORD_LENGTH"),
        max_length = getenv("MAX_PASSWORD_LENGTH")
    ) = Field(
        description = "The password"
    )

    not_before: Union[int, None] = Field(
        description = "The JWT not before date in unix timestamp",
        default = None
    )
    
    expire_at: Union[int, None] = Field(
        description = "The JWT expiration date in unix timestamp",
        default = None
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

    @model_validator(mode = 'after')
    def validate_not_before_before_expire_at(self) -> 'Login':
        """
        Validate that not_before is before expire_at if both are provided.
        
        Returns:
            Login: The validated instance.
            
        Raises:
            ValueError: If not_before is after expire_at.
        """
        if self.not_before is not None and self.expire_at is not None and self.not_before > self.expire_at:
            raise ValueError("Not before date must be before expiration date")
        return self

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
            self.phone_number is not None
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
                elif self.email is not None:
                    user = db.query(User).filter(
                        User.email == self.email,
                        User.deleted_at.is_(None)
                    ).first()
                else:  # phone_number is not None
                    user = db.query(User).filter(
                        User.phone_number == self.phone_number,
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
            status_code = 200,
            fields = {
                "jwt": encode(
                    claims,
                    secret,
                    algorithm = getenv("JWT_ALGORITHM")
                ),
                "expires_at": self.expire_at,
            },
        )
