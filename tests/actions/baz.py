from pydantic import Field
from core.action_runner import ActionRunner

class Baz(ActionRunner):
    foo: str = Field(description = "The foo value", default = None)
    bar: str = Field(description = "The bar value", default = None)

    @classmethod
    def description(self) -> str:
        return "This is a Baz test action"

    async def run(self) -> str:
        return f"{self.foo} {self.bar}"
