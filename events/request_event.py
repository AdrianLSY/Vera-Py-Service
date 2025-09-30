from json import dumps
from typing import TYPE_CHECKING, Any, Literal, override

from pydantic import Field, ValidationError
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner
from core.action_schema import ActionSchema

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
    class Payload(ActionSchema):
        """
        Represents the payload for a request event.

        Attributes:
            action (str): The name of the action to run.
            fields (dict): The fields to pass to the action.
            response_ref (str | None): The reference to send a response for the request.
        """
        action: str = Field(description = "The name of the action to run.")
        fields: dict[str, Any] = Field(description = "The fields to pass to the action.")
        response_ref: str | None = Field(description = "The reference to send a response for the request.", default = None)

        @classmethod
        @override
        def description(cls) -> str:
            return "Represents the payload for a request event."

    ref: str | None = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["request"] = Field(description = "A literal indicating the event type \"request\".", default = "request")
    payload: Payload = Field(description = "The payload containing the request information.")

    @classmethod
    @override
    def discriminator(cls) -> str:
        return "request"

    @classmethod
    @override
    def description(cls) -> str:
        return "Represents a request event to be be handled by the corresponding action runner."

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        try:
            response = await client.actions[self.payload.action](**self.payload.fields).run(client, websocket)
        except KeyError:
            response = ActionResponse(
                status_code = 404,
                message = f"Unknown action: {self.payload.action}",
            )
        except ValidationError:
            response = ActionResponse(
                status_code = 400,
                message = "Invalid request. Please check the required fields and try again."
            )
        except Exception:
            response = ActionResponse(
                status_code = 500,
                message = "Internal server error"
            )
        await websocket.send(
            dumps(
                {
                    "topic": self.topic,
                    "event": "response",
                    "payload": response.model_dump(),
                    "ref": self.payload.response_ref
                }
            )
        )
        return response
