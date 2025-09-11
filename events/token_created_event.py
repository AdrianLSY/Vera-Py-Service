from typing import TYPE_CHECKING, Literal, override

from pydantic import Field
from websockets import ClientConnection

from core.action_model import ActionModel
from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from models.token import Token

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class TokenCreatedEvent(ActionRunner):
    """
    Represents an event indicating that a token has been created.

    Attributes:
        ref (str | None): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["token_created"]): A literal indicating the event type "token_created".
        payload (Payload): The payload containing the token information.
    """
    class Payload(ActionModel):
        """
        Represents the payload for a token event.

        Attributes:
            token (Token): The token information.
        """
        token: Token = Field(description = "The token information.")

        @classmethod
        @override
        def description(cls) -> str:
            return "Represents the payload for a token event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["token_created"] = Field(description = "A literal indicating the event type \"token_created\".", default = "token_created")
    payload: Payload = Field(description = "The payload containing the token information.")

    @classmethod
    @override
    def discriminator(cls) -> str:
        return "token_created"

    @classmethod
    @override
    def description(cls) -> str:
        return "Represents an event indicating that a token has been created."

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        client.token = self.payload.token
        return ActionResponse(
            status_code = 200
        )
