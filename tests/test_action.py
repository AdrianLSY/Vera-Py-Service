import unittest
from core.actions import Action
from pydantic import Field, ValidationError

class Foo(Action):
    foo: str = Field(description = "The foo value", default = "Foo")
    bar: str = Field(description = "The bar value", default = "Bar")

    def description(self) -> str:
        return "This is a Foo test action"

    def run(self) -> str:
        return f"{self.foo} {self.bar}"


class Bar(Action):
    foo: str = Field(description = "The foo value")
    bar: str = Field(description = "The bar value")

    def description(self) -> str:
        return "This is a Bar test action"

    def run(self) -> str:
        return f"{self.foo} {self.bar}"


class Baz(Action):
    foo: str = Field(description = "The foo value", default = None)
    bar: str = Field(description = "The bar value", default = None)

    def description(self) -> str:
        return "This is a Baz test action"

    def run(self) -> str:
        return f"{self.foo} {self.bar}"


class TestAction(unittest.TestCase):
    def test_foo(self):
        foo = Foo()
        self.assertEqual(foo.run(), "Foo Bar")
        self.assertEqual(foo.description(), "This is a Foo test action")
        self.assertEqual(foo.model_json(), """{"Foo": {"description": "This is a Foo test action", "fields": {"foo": {"type": "string", "description": "The foo value", "default": "Foo"}, "bar": {"type": "string", "description": "The bar value", "default": "Bar"}}}}""")

        foo = Foo(foo = "Hello", bar = "World")
        self.assertEqual(foo.run(), "Hello World")
        self.assertEqual(foo.description(), "This is a Foo test action")
        self.assertEqual(foo.model_json(), """{"Foo": {"description": "This is a Foo test action", "fields": {"foo": {"type": "string", "description": "The foo value", "default": "Foo"}, "bar": {"type": "string", "description": "The bar value", "default": "Bar"}}}}""")
        print(foo.model_json(indent=2))

    def test_bar(self):
        try:
            bar = Bar()
        except ValidationError:
            pass
        else:
            raise ValidationError("Bar should not be valid")

        bar = Bar(foo = "Hello", bar = "World")
        self.assertEqual(bar.run(), "Hello World")
        self.assertEqual(bar.description(), "This is a Bar test action")
        self.assertEqual(bar.model_json(), """{"Bar": {"description": "This is a Bar test action", "fields": {"foo": {"type": "string", "description": "The foo value"}, "bar": {"type": "string", "description": "The bar value"}}}}""")

    def test_baz(self):
        baz = Baz()
        self.assertEqual(baz.run(), "None None")
        self.assertEqual(baz.description(), "This is a Baz test action")
        self.assertEqual(baz.model_json(), """{"Baz": {"description": "This is a Baz test action", "fields": {"foo": {"type": "string", "description": "The foo value", "default": null}, "bar": {"type": "string", "description": "The bar value", "default": null}}}}""")

        baz = Baz(foo = "Hello", bar = "World")
        self.assertEqual(baz.run(), "Hello World")
        self.assertEqual(baz.description(), "This is a Baz test action")
        self.assertEqual(baz.model_json(), """{"Baz": {"description": "This is a Baz test action", "fields": {"foo": {"type": "string", "description": "The foo value", "default": null}, "bar": {"type": "string", "description": "The bar value", "default": null}}}}""")


if __name__ == '__main__':
    unittest.main()
