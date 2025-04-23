from pydantic import Field
from typing import Literal
from core.models import Token
from core.actions import ActionRunner, ActionModel

class TokenCreatedEvent(ActionRunner):
    """
    Represents an event indicating that a token has been created.

    Attributes:
        ref (Optional[str]): A reference identifier for the event.
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

        def description(self) -> str:
            return "Represents the payload for a token event."

    ref: str = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["token_created"] = Field(description = "A literal indicating the event type \"token_created\".")
    payload: Payload = Field(description = "The payload containing the token information.")

    def description(self) -> str:
        return "Represents an event indicating that a token has been created."

    def run(self) -> str:
        print(self.model_dump_json(indent = 4))
