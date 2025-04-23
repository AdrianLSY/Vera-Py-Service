from pydantic import Field
from typing import Literal
from core.models import Service
from core.actions import ActionRunner, ActionModel

class ServiceDeletedEvent(ActionRunner):
    """
    Represents an event indicating that a service has been deleted.

    Attributes:
        ref (Optional[str]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["service_deleted"]): A literal indicating the event type "service_deleted".
        payload (Payload): The payload containing the service information that was deleted.
    """
    class Payload(ActionModel):
        """
        Represents the payload for a service deletion event.

        Attributes:
            service (Service): The service information that was deleted.
        """
        service: Service = Field(description = "The service information that was deleted.")

        def description(self) -> str:
            return "Represents the payload for a service deletion event."

    ref: str = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["service_deleted"] = Field(description = "A literal indicating the event type \"service_deleted\".")
    payload: Payload = Field(description = "The payload containing the service information that was deleted.")

    def description(self) -> str:
        return "Represents an event indicating that a service has been deleted."

    def run(self) -> str:
        print(self.model_dump_json(indent = 4))
