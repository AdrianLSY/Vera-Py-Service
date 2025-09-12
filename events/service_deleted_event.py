from typing import TYPE_CHECKING, Literal, override

from pydantic import Field
from websockets import ClientConnection

from core.action_schema import ActionSchema
from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from schemas.service import Service

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class ServiceDeletedEvent(ActionRunner):
    """
    Represents an event indicating that a service has been deleted.

    Attributes:
        ref (str | None): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["service_deleted"]): A literal indicating the event type "service_deleted".
        payload (Payload): The payload containing the service information that was deleted.
    """
    class Payload(ActionSchema):
        """
        Represents the payload for a service deletion event.

        Attributes:
            service (Service): The service information that was deleted.
        """
        service: Service = Field(description = "The service information that was deleted.")

        @classmethod
        @override
        def description(cls) -> str:
            return "Represents the payload for a service deletion event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["service_deleted"] = Field(description = "A literal indicating the event type \"service_deleted\".", default = "service_deleted")
    payload: Payload = Field(description = "The payload containing the service information that was deleted.")

    @classmethod
    @override
    def discriminator(cls) -> str:
        return "service_deleted"

    @classmethod
    @override
    def description(cls) -> str:
        return "Represents an event indicating that a service has been deleted."

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        await websocket.close()
        raise ConnectionAbortedError
