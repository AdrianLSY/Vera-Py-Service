from typing import TYPE_CHECKING, Literal, override

from pydantic import Field
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.action_schema import ActionSchema

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class PhxJoinEvent(ActionRunner):
    """
    Represents a Phoenix join event.

    Attributes:
        ref (str | None): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["phx_join"]): A literal indicating the event type "phx_join".
        payload (Payload): The payload of the join event.
    """
    class Payload(ActionSchema):
        """
        Represents the payload for a Phoenix join event.
        The payload is empty and is only used for the event.
        """
        pass

        @classmethod
        @override
        def description(cls) -> str:
            return "Represents the payload for a Phoenix join event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["phx_join"] = Field(description = "A literal indicating the event type \"phx_join\".", default = "phx_join")
    payload: Payload = Field(description = "The payload of the join event.", default = Payload())

    @classmethod
    @override
    def discriminator(cls) -> str:
        return "phx_join"

    @classmethod
    @override
    def description(cls) -> str:
        return "Represents a Phoenix join event."

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        return ActionResponse(
            status_code = 200
        )
