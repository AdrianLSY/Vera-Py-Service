from os import getenv
from typing import TYPE_CHECKING, Any, Dict, override

from jwt import InvalidTokenError, decode  # type: ignore
from pydantic import Field
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.database import database
from models.revocation import Revocation
from models.user import User

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Show(ActionRunner):
    jwt: str = Field(
        description = "The JWT token to authenticate"
    )

    @classmethod
    @override
    def description(cls) -> str:
        return "Authenticates the provided JWT token and returns user details"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:

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

                # get user details
                user = db.query(User).filter(
                    User.id == user_id,
                    User.deleted_at.is_(None)
                ).first()

                if not user:
                    return ActionResponse(
                        status_code = 404,
                        message = "User not found"
                    )

        except Exception as e:
            return ActionResponse(
                status_code = 500,
                message = f"Database error: {str(e)}"
            )

        return ActionResponse(
            status_code = 200,
            fields = {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "created_at": int(user.created_at.timestamp()),
                    "updated_at": int(user.updated_at.timestamp()),
                    },
                "claims": claims
            }
        )
