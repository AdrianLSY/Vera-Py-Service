from typing import TYPE_CHECKING, override, Union

from pydantic import Field, constr
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

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Edit(ActionRunner):
    jwt: str = Field(description = "The JWT token for authentication")
    username: Union[constr(min_length = getenv("MIN_USERNAME_LENGTH"), max_length = getenv("MAX_USERNAME_LENGTH")), None] = Field(description = "The new username", default = None)
    password: Union[constr(min_length = getenv("MIN_PASSWORD_LENGTH"), max_length = getenv("MAX_PASSWORD_LENGTH")), None] = Field(description = "The new password", default = None)

    @classmethod
    @override
    def description(cls) -> str:
        return "Updates user username and/or password using JWT authentication"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        
        # validate that at least one field is provided
        if self.username is None and self.password is None:
            return ActionResponse(
                status_code = 400,
                message = "At least one field (username or password) must be provided"
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
                
                if self.password is not None:
                    user.password_digest = hashpw(
                        self.password.encode("utf-8"),
                        gensalt()
                    ).decode("utf-8")
                
                db.flush()  # ensure changes are persisted
                
        except IntegrityError:
            # username unique violation
            return ActionResponse(
                status_code = 409,
                message = "Username already taken"
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
