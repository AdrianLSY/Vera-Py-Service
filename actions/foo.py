from pydantic import Field
from core.action_runner import ActionRunner

class Foo(ActionRunner):
    foo: str = Field(description = "The foo value", default = "Foo")
    bar: str = Field(description = "The bar value", default = "Bar")

    @classmethod
    def description(self) -> str:
        return "This is a Foo test action"

    async def run(self) -> str:
        return f"{self.foo} {self.bar}"
