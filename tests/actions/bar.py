from pydantic import Field
from typing import TYPE_CHECKING
from websockets import ClientConnection
from core.action_runner import ActionRunner
from core.action_response import ActionResponse

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Bar(ActionRunner):
    foo: str = Field(description = "The foo value")
    bar: str = Field(description = "The bar value")

    @classmethod
    def description(cls) -> str:
        return "This is a Bar test action"

    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        return ActionResponse(
            status_code = 200,
            fields = f"{self.foo} {self.bar}"
        )
