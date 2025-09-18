from os import getenv
from typing import TYPE_CHECKING, Any, Dict, Union, override

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


class Delete(ActionRunner):
    """
    Action to soft delete a user by setting deleted_at timestamp.

    This action supports authentication via either JWT token or user_id.
    At least one authentication method must be provided.
    """

    jwt: Union[str, None] = Field(
        description = "Optional JWT token to query the user. pass this or user_id",
        default = None
    )

    user_id: Union[int, None] = Field(
        description = "Optional user ID to query the user. pass this or the jwt",
        default = None
    )

    @classmethod
    @override
    def description(cls) -> str:
        return "Soft deletes a user by setting deleted_at timestamp using JWT or user_id authentication"

    def __validate_jwt(self) -> Union[int, ActionResponse]:
        """
        Validate JWT token and extract user_id.

        Returns:
            Union[int, ActionResponse]: User ID if valid, ActionResponse with error if invalid.
        """
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
        """
        Soft delete a user by setting deleted_at timestamp.

        Returns:
            ActionResponse: Success or error response.
        """
        user_id = self.user_id

        # validate if jwt or user_id is provided
        if self.jwt is None and self.user_id is None:
            return ActionResponse(
                status_code = 400,
                message = "Either JWT or user_id must be provided"
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

                # soft delete user by setting deleted_at
                from datetime import datetime, timezone
                user.deleted_at = datetime.now(timezone.utc)
                db.flush()  # ensure changes are persisted

        except Exception as e:
            return ActionResponse(
                status_code = 500,
                message = f"Database error: {str(e)}"
            )

        return ActionResponse(
            status_code = 200,
            message = "User deleted successfully"
        )
