from typing import TYPE_CHECKING, override, Union

from pydantic import Field, constr
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

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Login(ActionRunner):
    username: constr(min_length = getenv("MIN_USERNAME_LENGTH"), max_length = getenv("MAX_USERNAME_LENGTH")) = Field(description = "The username")
    password: constr(min_length = getenv("MIN_PASSWORD_LENGTH"), max_length = getenv("MAX_PASSWORD_LENGTH")) = Field(description = "The password")
    not_before: Union[int, None] = Field(description = "The JWT not before date in unix timestamp", default = None)
    expire_at: Union[int, None] = Field(description = "The JWT expiration date in unix timestamp", default = None)

    @classmethod
    @override
    def description(cls) -> str:
        return "Generates a JWT token for an existing user"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        
        # sanity check
        if self.not_before is not None and self.expire_at is not None and self.not_before > self.expire_at:
            return ActionResponse(
                status_code = 400,
                message = "Not before date must be before expiration date"
            )

        # lookup user and verify password
        try:
            with database.transaction() as db:
                user = db.query(User).filter(
                    User.username == self.username,
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
