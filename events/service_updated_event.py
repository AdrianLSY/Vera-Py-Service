from pydantic import Field
from typing import Literal
from core.models import Service
from core.actions import ActionRunner, ActionModel

class ServiceUpdatedEvent(ActionRunner):
    """
    Represents an event indicating that a service has been updated.

    Attributes:
        ref (Optional[str]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["service_updated"]): A literal indicating the event type "service_updated".
        payload (Payload): The payload containing updated service information.
    """
    class Payload(ActionModel):
        """
        Represents the payload for a service update event.

        Attributes:
            service (Service): The updated service information.
        """
        service: Service = Field(description = "The updated service information.")

        def description(self) -> str:
            return "Represents the payload for a service update event."

    ref: str = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["service_updated"] = Field(description = "A literal indicating the event type \"service_updated\".")
    payload: Payload = Field(description = "The payload containing updated service information.")

    def description(self) -> str:
        return "Represents an event indicating that a service has been updated."

    def run(self) -> str:
        print(self.model_dump_json(indent = 4))
