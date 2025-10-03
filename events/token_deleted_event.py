from typing import Literal

from pydantic import Field

from core.action_schema import ActionSchema
from core.action_event import ActionEvent
from schemas.token import Token

class TokenDeletedEvent(ActionEvent):
    """
    Represents an event when a token has been created.

    Attributes:
        ref (str | None): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["token_deleted"]): A literal indicating the event type "token_deleted".
        payload (Payload): The payload containing the token information.
    """
    class Payload(ActionSchema):
        """
        Represents the payload for a token event.

        Attributes:
            token (Token): The token information.
        """
        token: Token = Field(description = "The token information.")

        @classmethod
        def description(cls) -> str:
            return "Represents the payload for a token event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["token_deleted"] = Field(description = "A literal indicating the event type \"token_deleted\".", default = "token_deleted")
    payload: Payload = Field(description = "The payload containing the token information.")

    @classmethod
    def discriminator(cls) -> str:
        return "token_deleted"

    @classmethod
    def description(cls) -> str:
        return "Represents an event when a token has been created."
