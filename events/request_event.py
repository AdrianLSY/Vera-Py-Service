from json import dumps
from pydantic import Field
from websockets import ClientConnection
from typing import Literal, TYPE_CHECKING
from core.action_model import ActionModel
from core.action_runner import ActionRunner

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class RequestEvent(ActionRunner):
    """
    Represents a request event to be be handled by the corresponding action runner.

    Attributes:
        ref (str | None): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["request"]): A literal indicating the event type "request".
        payload (Payload): The payload containing the request information.
    """
    class Payload(ActionModel):
        """
        Represents the payload for a request event.

        Attributes:
            action (str): The name of the action to run.
            fields (dict): The fields to pass to the action.
            response_ref (str | None): The reference to send a response for the request.
        """
        action: str = Field(description = "The name of the action to run.")
        fields: dict = Field(description = "The fields to pass to the action.")
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

    async def run(self, client: PlugboardClient, websocket: ClientConnection) -> None:
        try:
            response = {
                "message": await client.actions[self.payload.action](**self.payload.fields).run(client, websocket),
                "status": "success"
            }
            dumps(response)
        except KeyError:
            response = {
                "message": f"Unknown action: {self.payload.action}",
                "status": "error"
            }
        except TypeError:
            response = {
                "message": "Client sent an invalid response",
                "status": "error"
            }
        await websocket.send(
            dumps(
                {
                    "topic": self.topic,
                    "event": "response",
                    "payload": response,
                    "ref": self.payload.response_ref
                }
            )
        )
