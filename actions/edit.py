from typing import TYPE_CHECKING, override, Union

from pydantic import Field, constr, EmailStr, field_validator
from websockets import ClientConnection
from jwt import decode, InvalidTokenError
from os import getenv
from bcrypt import hashpw, gensalt
from sqlalchemy.exc import IntegrityError

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.database import database
from models.user import User
from models.revocation import Revocation
import phonenumbers
from phonenumbers import NumberParseException

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Edit(ActionRunner):
    jwt: str = Field(
        description = "The JWT token for authentication"
    )

    username: Union[
        constr(
            min_length = getenv("MIN_USERNAME_LENGTH"),
            max_length = getenv("MAX_USERNAME_LENGTH")
        ),
        None
    ] = Field(
        description = "The new username",
        default = None
    )

    name: Union[
        constr(
            min_length = 1,
            max_length = 255
        ),
        None
    ] = Field(
        description = "The new name",
        default = None
    )

    email: Union[EmailStr, None] = Field(
        description = "The new email address",
        default = None
    )

    phone_number: Union[str, None] = Field(
        description = "The new phone number in any format (will be converted to E.164)",
        default = None
    )

    password: Union[
        constr(
            min_length = getenv("MIN_PASSWORD_LENGTH"),
            max_length = getenv("MAX_PASSWORD_LENGTH")
        ),
        None
    ] = Field(
        description = "The new password",
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

    @classmethod
    @override
    def description(cls) -> str:
        return "Updates user username and/or password using JWT authentication"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        
        # validate that at least one field is provided
        if self.username is None and self.name is None and self.email is None and self.phone_number is None and self.password is None:
            return ActionResponse(
                status_code = 400,
                message = "At least one field (username, name, email, phone_number, or password) must be provided"
            )

        # decode and validate JWT
        secret = getenv("JWT_SECRET")
        if not secret:
            return ActionResponse(
                status_code = 500,
                message = "Missing JWT secret"
            )

        try:
            # decode JWT with validation
            claims = decode(
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

        # check if token is revoked
        try:
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
