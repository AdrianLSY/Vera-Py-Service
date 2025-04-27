from pydantic import Field
from models.service import Service
from websockets import ClientConnection
from typing import Literal, TYPE_CHECKING
from core.action_model import ActionModel
from core.action_runner import ActionRunner

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class ServiceUpdatedEvent(ActionRunner):
    """
    Represents an event indicating that a service has been updated.

    Attributes:
        ref (str | None): A reference identifier for the event.
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

        @classmethod
        def description(cls) -> str:
            return "Represents the payload for a service update event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["service_updated"] = Field(description = "A literal indicating the event type \"service_updated\".", default = "service_updated")
    payload: Payload = Field(description = "The payload containing updated service information.")

    @classmethod
    def discriminator(cls) -> str:
        return "service_updated"

    @classmethod
    def description(cls) -> str:
        return "Represents an event indicating that a service has been updated."

    async def run(self, client: PlugboardClient, websocket: ClientConnection) -> None:
        client.service = self.payload.service
