from typing import TYPE_CHECKING, override

from pydantic import Field
from websockets import ClientConnection
from jwt import decode, InvalidTokenError
from os import getenv
from sqlalchemy.exc import IntegrityError

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.database import database
from models.revocation import Revocation

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Logout(ActionRunner):
    jwt: str = Field(description = "The JWT token to revoke")

    @classmethod
    @override
    def description(cls) -> str:
        return "Revokes the provided JWT token by adding it to the revocations table"

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
            payload = decode(
                self.jwt,
                secret,
                algorithms = [getenv("JWT_ALGORITHM", "HS256")],
                audience = getenv("JWT_AUDIENCE"),
                issuer = getenv("JWT_ISSUER")
            )
            
            jti = payload.get("jti")
            
            if not jti:
                return ActionResponse(
                    status_code = 401,
                    message = "Invalid token: missing JTI claim"
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

        # add to revocations table
        try:
            with database.transaction() as db:
                revocation = Revocation(jti = jti)
                db.add(revocation)
                db.flush()  # ensure the record is created
                
        except IntegrityError:
            # JTI already exists in revocations (already revoked)
            return ActionResponse(
                status_code = 409,
                message = "Token has already been revoked"
            )
        except Exception as e:
            return ActionResponse(
                status_code = 500,
                message = f"Database error: {str(e)}"
            )

        return ActionResponse(
            status_code = 200,
            message = "Token successfully revoked"
        )
