from typing import Literal

from pydantic import Field

from core.action_schema import ActionSchema
from core.action_event import ActionEvent

class ConsumerConnectedEvent(ActionEvent):
    """
    Represents an event indicating that the number of consumers connected to the service has changed.

    Attributes:
        ref (str | None): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["num_consumers"]): A literal indicating the event type "num_consumers".
        payload (Payload): The payload containing the number of consumers connected to the service.
    """
    class Payload(ActionSchema):
        """
        Represents the payload for a consumers connected event.

        Attributes:
            num_consumers (int): The number of consumers connected to the service.
        """
        num_consumers: int = Field(description = "The number of consumers connected to the service.")

        @classmethod
        def description(cls) -> str:
            return "Represents the payload for a consumers connected event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["num_consumers"] = Field(description = "A literal indicating the event type \"num_consumers\".", default = "num_consumers")
    payload: Payload = Field(description = "The payload containing the number of consumers connected to the service.")

    @classmethod
    def discriminator(cls) -> str:
        return "num_consumers"

    @classmethod
    def description(cls) -> str:
        return "Represents an event indicating that the number of consumers connected to the service has changed."
