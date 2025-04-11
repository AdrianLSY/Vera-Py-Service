from pydantic import Field
from core.actions import ActionModel, ActionRunner

class Foo(ActionModel):
    foo: str = Field(description = "The foo value", default = "Foo")
    bar: str = Field(description = "The bar value", default = "Bar")

    @classmethod
    def description(self) -> str:
        return "This is a Foo test action"


class Bar(ActionModel):
    foo: str = Field(description = "The foo value")
    bar: str = Field(description = "The bar value")

    @classmethod
    def description(self) -> str:
        return "This is a Bar test action"


class Baz(ActionModel):
    foo: str = Field(description = "The foo value", default = None)
    bar: str = Field(description = "The bar value", default = None)

    @classmethod
    def description(self) -> str:
        return "This is a Baz test action"


class FooBarBaz(ActionRunner):
    foo: Foo = Field(description = "The Foo value")
    bar: Bar = Field(description = "The Bar value")
    baz: Baz = Field(description = "The Baz value")
    hello: str = Field(description = "The hello value", default = "Hello")
    world: str = Field(description = "The world value", default = "World")

    @classmethod
    def description(self) -> str:
        return "This is a FooBarBaz test action"

    def run(self) -> str:
        foo = f"{self.foo.foo} {self.foo.bar}"
        bar = f"{self.bar.foo} {self.bar.bar}"
        baz = f"{self.baz.foo} {self.baz.bar}"
        return f"{foo} {bar} {baz}"
