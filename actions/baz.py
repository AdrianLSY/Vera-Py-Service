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

class Baz(ActionRunner):
    foo: str | None = Field(description = "The foo value", default = None)
    bar: str | None = Field(description = "The bar value", default = None)

    @classmethod
    @override
    def description(cls) -> str:
        return "This is a Baz test action"

    @override
    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        return ActionResponse(
            status_code = 200,
            fields = f"{self.foo} {self.bar}"
        )
