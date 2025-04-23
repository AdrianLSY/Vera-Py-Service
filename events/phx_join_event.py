from typing import Literal
from pydantic import Field
from core.actions import ActionRunner, ActionModel

class PhxJoinEvent(ActionRunner):
    """
    Represents a Phoenix join event.

    Attributes:
        ref (Optional[str]): A reference identifier for the event.
        topic (str): The topic to which the event is associated.
        event (Literal["phx_join"]): A literal indicating the event type "phx_join".
        payload (Payload): The payload of the join event.
    """
    class Payload(ActionModel):
        """
        Represents the payload for a Phoenix join event.

        Attributes:
            None: This model does not include any fields.
        """
        pass

        def description(self) -> str:
            return "Represents the payload for a Phoenix join event."

    ref: str = Field(description = "A reference identifier for the event.", default = None)
    topic: str = Field(description = "The topic to which the event is associated.")
    event: Literal["phx_join"] = Field(description = "A literal indicating the event type \"phx_join\".")
    payload: Payload = Field(description = "The payload of the join event.")

    def description(self) -> str:
        return "Represents a Phoenix join event."

    def run(self) -> str:
        print(self.model_dump_json(indent = 4))
