from typing import Any, Literal

from pydantic import Field

from core.action_event import ActionEvent
from core.action_schema import ActionSchema

class RequestEvent(ActionEvent):
    """
    Represents a request event to be be handled by the corresponding action runner.

    Attributes:
        ref (str | None): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["request"]): A literal indicating the event type "request".
        payload (Payload): The payload containing the request information.
    """
    class Payload(ActionSchema):
        """
        Represents the payload for a request event.

        Attributes:
            action (str): The name of the action to run.
            fields (dict): The fields to pass to the action.
            response_ref (str | None): The reference to send a response for the request.
        """
        action: str = Field(description = "The name of the action to run.")
        fields: dict[str, Any] = Field(description = "The fields to pass to the action.")
        response_ref: str | None = Field(description = "The reference to send a response for the request.", default = None)

        @classmethod
        def description(cls) -> str:
            return "Represents the payload for a request event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["request"] = Field(description = "A literal indicating the event type \"request\".", default = "request")
    payload: Payload = Field(description = "The payload containing the request information.")

    @classmethod
    def discriminator(cls) -> str:
        return "request"

    @classmethod
    def description(cls) -> str:
        return "Represents a request event to be be handled by the corresponding action runner."
