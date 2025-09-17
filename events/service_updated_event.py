from typing import TYPE_CHECKING, Literal, override

from pydantic import Field
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.action_schema import ActionSchema
from schemas.service import Service

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
    class Payload(ActionSchema):
        """
        Represents the payload for a service update event.

        Attributes:
            service (Service): The updated service information.
        """
        service: Service = Field(description = "The updated service information.")

        @classmethod
        @override
        def description(cls) -> str:
            return "Represents the payload for a service update event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["service_updated"] = Field(description = "A literal indicating the event type \"service_updated\".", default = "service_updated")
    payload: Payload = Field(description = "The payload containing updated service information.")

    @classmethod
    @override
    def discriminator(cls) -> str:
        return "service_updated"

    @classmethod
    @override
    def description(cls) -> str:
        return "Represents an event indicating that a service has been updated."

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        client.service = self.payload.service
        return ActionResponse(
            status_code = 200
        )
