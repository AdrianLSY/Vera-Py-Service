from typing import TYPE_CHECKING, override

from pydantic import Field, constr
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

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Register(ActionRunner):
    username: constr(min_length = getenv("MIN_USERNAME_LENGTH"), max_length = getenv("MAX_USERNAME_LENGTH")) = Field(description = "The username")
    password: constr(min_length = getenv("MIN_PASSWORD_LENGTH"), max_length = getenv("MAX_PASSWORD_LENGTH")) = Field(description = "The password")
    not_before: Union[int, None] = Field(description = "The JWT not before date in unix timestamp", default = None)
    expire_at: Union[int, None] = Field(description = "The JWT expiration date in unix timestamp", default = None)

    @classmethod
    @override
    def description(cls) -> str:
        return "Creates a new user and returns the associated jwt token"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        
        # sanity check
        if self.not_before is not None and self.expire_at is not None and self.not_before > self.expire_at:
            return ActionResponse(
                status_code = 400,
                message = "Not before date must be before expiration date"
            )

        # insert user
        try:
            with database.transaction() as db:
                user = User(
                    username = self.username,
                    password_digest = hashpw(
                        self.password.encode("utf-8"),
                        gensalt()
                    ).decode("utf-8")
                )
                db.add(user)
                db.flush()  # assign id without ending txn
                user_id = user.id
        except IntegrityError:
            # username unique violation
            return ActionResponse(
                status_code = 409,
                message = "Username already taken"
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