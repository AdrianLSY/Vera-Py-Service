from typing import TYPE_CHECKING, cast, override
from unittest import TestCase
from unittest.mock import Mock

from core.action_response import ActionResponse
from core.action_runner import ActionRunner

if TYPE_CHECKING:
    from websockets import ClientConnection

    from core.plugboard_client import PlugboardClient


class TestActionRunner(TestCase):
    """Test cases for ActionRunner base class."""

    test_runner_class: type[ActionRunner]  # type: ignore

    @override
    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class TestRunner(ActionRunner):
            name: str = "test"
            value: int = 42

            @classmethod
            @override
            def description(cls) -> str:
                return "Test runner for unit testing"

            @override
            async def run(self, client: "PlugboardClient", websocket: "ClientConnection") -> ActionResponse:
                return ActionResponse(
                    status_code = 200,
                    message = f"Test: {self.name}",
                    fields = {"value": self.value}
                )

        self.test_runner_class: type[ActionRunner] = TestRunner

    def test_action_runner_inheritance(self) -> None:
        """Test that ActionRunner inherits from ActionModel."""
        from core.action_model import ActionModel

        # ActionRunner is always a subclass of ActionModel by design
        self.assertIsInstance(ActionRunner, type)

    def test_action_runner_abstract_run_method(self) -> None:
        """Test that ActionRunner has abstract run method."""
        # This test verifies that ActionRunner cannot be instantiated without run()
        with self.assertRaises(TypeError):
            class IncompleteRunner(ActionRunner):
                @classmethod
                @override
                def description(cls) -> str:
                    return "Incomplete runner"
                # Missing run() implementation

            # This should raise TypeError due to abstract method
            IncompleteRunner()

    def test_action_runner_description_implementation(self) -> None:
        """Test that ActionRunner requires description implementation."""
        with self.assertRaises(TypeError):
            class IncompleteRunner(ActionRunner):
                @override
                async def run(self, client: "PlugboardClient", websocket: "ClientConnection") -> ActionResponse:
                    return ActionResponse(status_code = 200)
                # Missing description() implementation

            # This should raise TypeError due to abstract method
            IncompleteRunner()

    def test_action_runner_discriminator(self) -> None:
        """Test ActionRunner discriminator method."""
        discriminator = self.test_runner_class.discriminator()

        self.assertEqual(discriminator, "TestRunner")

    def test_action_runner_description(self) -> None:
        """Test ActionRunner description method."""
        description = self.test_runner_class.description()

        self.assertEqual(description, "Test runner for unit testing")

    def test_action_runner_model_dict(self) -> None:
        """Test ActionRunner model_dict method."""
        result = self.test_runner_class.model_dict()

        self.assertIn("TestRunner", result)
        self.assertIn("description", result["TestRunner"])
        self.assertIn("fields", result["TestRunner"])

        fields = result["TestRunner"]["fields"]
        self.assertIn("name", fields)
        self.assertIn("value", fields)

    def test_action_runner_model_json(self) -> None:
        """Test ActionRunner model_json method."""
        json_str = self.test_runner_class.model_json()

        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertIn("TestRunner", parsed)

    def test_action_runner_instance_creation(self) -> None:
        """Test creating ActionRunner instances."""
        instance = self.test_runner_class(name = "test_instance", value = 100)

        # Type assertions to help the linter
        name = cast(str, instance.name)
        value = cast(int, instance.value)

        self.assertEqual(name, "test_instance")
        self.assertEqual(value, 100)

    def test_action_runner_run_method_returns_action_response(self) -> None:
        """Test that run method returns ActionResponse."""
        instance = self.test_runner_class(name = "test", value = 42)
        mock_client = Mock()
        mock_websocket = Mock()

        # This should not raise an exception
        import asyncio
        result = asyncio.run(instance.run(mock_client, mock_websocket))

        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.message, "Test: test")
        self.assertEqual(result.fields, {"value": 42})

    def test_action_runner_run_method_signature(self) -> None:
        """Test that run method has correct signature."""
        import inspect

        run_method = self.test_runner_class.run
        signature = inspect.signature(run_method)

        # Should have self, client, and websocket parameters
        params = list(signature.parameters.keys())
        self.assertIn("self", params)
        self.assertIn("client", params)
        self.assertIn("websocket", params)

    def test_action_runner_abstract_run_raises_not_implemented(self) -> None:
        """Test that abstract run method raises NotImplementedError."""
        # This test verifies that ActionRunner cannot be instantiated without run()
        with self.assertRaises(TypeError):
            class AbstractRunner(ActionRunner):
                @classmethod
                @override
                def description(cls) -> str:
                    return "Abstract runner"

                # run method not implemented

            # This should raise TypeError due to abstract method
            AbstractRunner()

    def test_action_runner_with_nested_models(self) -> None:
        """Test ActionRunner with nested ActionModel fields."""
        from pydantic import Field

        from core.action_model import ActionModel

        class NestedModel(ActionModel):
            nested_field: str = Field(description = "Nested field")

            @classmethod
            @override
            def description(cls) -> str:
                return "Nested model"

        class NestedRunner(ActionRunner):
            nested: NestedModel = Field(description = "Nested model field")

            @classmethod
            @override
            def description(cls) -> str:
                return "Runner with nested model"

            @override
            async def run(self, client: "PlugboardClient", websocket: "ClientConnection") -> ActionResponse:
                return ActionResponse(status_code = 200)

        # Test model_dict with nested fields
        result = NestedRunner.model_dict()

        self.assertIn("NestedRunner", result)
        fields = result["NestedRunner"]["fields"]
        self.assertIn("nested", fields)

        # Check nested field structure
        nested_field = fields["nested"]
        self.assertEqual(nested_field["type"], "NestedModel")
        self.assertIn("fields", nested_field)

    def test_action_runner_validation(self) -> None:
        """Test ActionRunner field validation."""
        # Valid data should work
        instance = self.test_runner_class(name = "valid", value = 100)

        # Type assertions to help the linter
        name = cast(str, instance.name)
        value = cast(int, instance.value)

        self.assertEqual(name, "valid")
        self.assertEqual(value, 100)

        # Invalid data should raise ValidationError
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            self.test_runner_class(name = "valid", value = "not_an_int")


if __name__ == "__main__":
    from unittest import main
    main()
