from pydantic import Field
from typing import TYPE_CHECKING
from websockets import ClientConnection
from core.action_runner import ActionRunner
from core.action_response import ActionResponse

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Baz(ActionRunner):
    foo: str | None = Field(description = "The foo value", default = None)
    bar: str | None = Field(description = "The bar value", default = None)

    @classmethod
    def description(cls) -> str:
        return "This is a Baz test action"

    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        return ActionResponse(
            status_code = 200,
            fields = f"{self.foo} {self.bar}"
        )
