from pydantic import Field
from typing import Literal
from core.actions import ActionRunner, ActionModel

class RequestEvent(ActionRunner):
    """
    Represents a request event to be be handled by the corresponding action runner.

    Attributes:
        ref (Optional[str]): A reference identifier for the event.
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
            response_ref (Optional[str]): The reference to send a response for the request.
        """
        action: str = Field(description = "The name of the action to run.")
        fields: dict = Field(description = "The fields to pass to the action.")
        response_ref: str = Field(description = "The reference to send a response for the request.", default = None)

        def description(self) -> str:
            return "Represents the payload for a request event."

    ref: str = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["request"] = Field(description = "A literal indicating the event type \"request\".")
    payload: Payload = Field(description = "The payload containing the request information.")

    def description(self) -> str:
        return "Represents a request event to be be handled by the corresponding action runner."

    def run(self) -> str:
        print(self.model_dump_json(indent = 4))
