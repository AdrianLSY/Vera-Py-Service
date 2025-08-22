from pydantic import Field
from typing import TYPE_CHECKING
from websockets import ClientConnection
from core.action_model import ActionModel
from core.action_runner import ActionRunner
from core.action_response import ActionResponse

if TYPE_CHECKING:
    from core.plugboard_client import PlugboardClient


class Foo(ActionModel):
    foo: str = Field(description = "The foo value", default = "Foo")
    bar: str = Field(description = "The bar value", default = "Bar")

    @classmethod
    def description(cls) -> str:
        return "This is a Foo test action"


class Bar(ActionModel):
    foo: str = Field(description = "The foo value")
    bar: str = Field(description = "The bar value")

    @classmethod
    def description(cls) -> str:
        return "This is a Bar test action"


class Baz(ActionModel):
    foo: str | None = Field(description = "The foo value", default = None)
    bar: str | None = Field(description = "The bar value", default = None)

    @classmethod
    def description(cls) -> str:
        return "This is a Baz test action"


class FooBarBaz(ActionRunner):
    foo: Foo = Field(description = "The Foo value")
    bar: Bar = Field(description = "The Bar value")
    baz: Baz = Field(description = "The Baz value")
    hello: str = Field(description = "The hello value", default = "Hello")
    world: str = Field(description = "The world value", default = "World")

    @classmethod
    def description(cls) -> str:
        return "This is a FooBarBaz test action"

    async def run(self, client: PlugboardClient, websocket: ClientConnection) -> ActionResponse:
        foo = f"{self.foo.foo} {self.foo.bar}"
        bar = f"{self.bar.foo} {self.bar.bar}"
        baz = f"{self.baz.foo} {self.baz.bar}"
        hello_world = f"{self.hello} {self.world}"
        return ActionResponse(
            status_code = 200,
            fields = f"{foo} {bar} {baz} {hello_world}"
        )
