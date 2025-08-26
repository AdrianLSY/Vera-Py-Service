from pydantic import Field
from typing import TYPE_CHECKING
from websockets import ClientConnection
from core.action_runner import ActionRunner
from core.action_response import ActionResponse

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient

class Foo(ActionRunner):
    foo: str = Field(description = "The foo value", default = "Foo")
    bar: str = Field(description = "The bar value", default = "Bar")

    @classmethod
    def description(cls) -> str:
        return "This is a Foo test action"

    async def run(self, client: "PlugboardClient", websocket: ClientConnection) -> ActionResponse:
        return ActionResponse(
            status_code = 200,
            fields = f"{self.foo} {self.bar}"
        )
