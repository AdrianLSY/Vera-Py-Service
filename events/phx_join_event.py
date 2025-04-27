from pydantic import Field
from websockets import ClientConnection
from typing import Literal, TYPE_CHECKING
from core.action_model import ActionModel
from core.action_runner import ActionRunner

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
    class Payload(ActionModel):
        """
        Represents the payload for a Phoenix join event.
        The payload is empty and is only used for the event.
        """
        pass

        @classmethod
        def description(cls) -> str:
            return "Represents the payload for a Phoenix join event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["phx_join"] = Field(description = "A literal indicating the event type \"phx_join\".", default = "phx_join")
    payload: Payload = Field(description = "The payload of the join event.", default = Payload())

    @classmethod
    def discriminator(cls) -> str:
        return "phx_join"

    @classmethod
    def description(cls) -> str:
        return "Represents a Phoenix join event."

    async def run(self, client: PlugboardClient, websocket: ClientConnection) -> None:
        pass
