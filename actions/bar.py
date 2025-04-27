from pydantic import Field
from core.action_runner import ActionRunner

class Bar(ActionRunner):
    foo: str = Field(description = "The foo value")
    bar: str = Field(description = "The bar value")

    @classmethod
    def description(self) -> str:
        return "This is a Bar test action"

    async def run(self) -> str:
        return f"{self.foo} {self.bar}"
