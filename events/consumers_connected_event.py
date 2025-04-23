from pydantic import Field
from typing import Literal
from core.actions import ActionRunner, ActionModel

class ConsumersConnectedEvent(ActionRunner):
    """
    Represents an event indicating that the number of consumers connected to the service has changed.

    Attributes:
        ref (Optional[str]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["num_consumers"]): A literal indicating the event type "num_consumers".
        payload (Payload): The payload containing the number of consumers connected to the service.
    """
    class Payload(ActionModel):
        """
        Represents the payload for a consumers connected event.

        Attributes:
            num_consumers (int): The number of consumers connected to the service.
        """
        num_consumers: int = Field(description = "The number of consumers connected to the service.")

        def description(self) -> str:
            return "Represents the payload for a consumers connected event."

    ref: str = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["num_consumers"] = Field(description = "A literal indicating the event type \"num_consumers\".")
    payload: Payload = Field(description = "The payload containing the number of consumers connected to the service.")

    def description(self) -> str:
        return "Represents an event indicating that the number of consumers connected to the service has changed."

    def run(self) -> str:
        print(self.model_dump_json(indent = 4))
