from typing import TYPE_CHECKING, override

from pydantic import Field
from websockets import ClientConnection

from core.action_response import ActionResponse
from core.action_runner import ActionRunner

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

"""
This serves as an example action that demonstrates how to create a new action.
"""

class Bar(ActionRunner):
    foo: str = Field(description = "The foo value")
    bar: str = Field(description = "The bar value")

    @classmethod
    @override
    def description(cls) -> str:
        return "This is a Bar test action"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        return ActionResponse(
            status_code = 200,
            fields = f"{self.foo} {self.bar}"
        )
