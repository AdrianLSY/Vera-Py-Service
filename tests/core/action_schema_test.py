from json import loads
from typing import cast, override
from unittest import TestCase

from pydantic import Field, ValidationError

from core.action_schema import ActionSchema


class TestActionSchema(TestCase):
    """Test cases for ActionSchema base class."""

    test_action_class: type[ActionSchema]  # type: ignore

    @override
    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class TestAction(ActionSchema):
            name: str = Field(description = "Test name field")
            value: int = Field(description = "Test value field", default = 42)
            optional: str | None = Field(description = "Optional field", default = None)

            @classmethod
            @override
            def description(cls) -> str:
                return "Test action for unit testing"

        self.test_action_class: type[ActionSchema] = TestAction

    def test_discriminator_returns_class_name(self) -> None:
        """
        Test that discriminator returns the class name.

        Returns:
            None: This test does not return a value.
        """
        self.assertEqual(self.test_action_class.discriminator(), "TestAction")

    def test_description_returns_implemented_description(self) -> None:
        """
        Test that description returns the implemented description.

        Returns:
            None: This test does not return a value.
        """
        self.assertEqual(self.test_action_class.description(), "Test action for unit testing")

    def test_to_dict_returns_correct_structure(self) -> None:
        """
        Test that to_dict returns the correct dictionary structure.

        Returns:
            None: This test does not return a value.
        """
        result = self.test_action_class.to_dict()

        self.assertIn("TestAction", result)
        self.assertIn("description", result["TestAction"])
        self.assertIn("fields", result["TestAction"])

        fields = result["TestAction"]["fields"]
        self.assertIn("name", fields)
        self.assertIn("value", fields)
        self.assertIn("optional", fields)

        # Check field structure
        name_field = fields["name"]
        self.assertEqual(name_field["type"], "string")
        self.assertEqual(name_field["description"], "Test name field")
        self.assertNotIn("default", name_field)

        value_field = fields["value"]
        self.assertEqual(value_field["type"], "integer")
        self.assertEqual(value_field["description"], "Test value field")
        self.assertEqual(value_field["default"], 42)

        optional_field = fields["optional"]
        self.assertIsNone(optional_field["type"])  # Optional fields have type None
        self.assertEqual(optional_field["description"], "Optional field")
        self.assertIsNone(optional_field.get("default"))

    def test_to_json_returns_valid_json(self) -> None:
        """
        Test that to_json returns valid JSON.

        Returns:
            None: This test does not return a value.
        """
        json_str = self.test_action_class.to_json()

        # Should be valid JSON
        parsed = loads(json_str)
        self.assertIsInstance(parsed, dict)
        self.assertIn("TestAction", parsed)

    def test_to_json_with_indent(self) -> None:
        """
        Test that to_json with indent returns formatted JSON.

        Returns:
            None: This test does not return a value.
        """
        json_str = self.test_action_class.to_json(indent = 2)

        # Should contain newlines for indentation
        self.assertIn("\n", json_str)

        # Should be valid JSON
        parsed = loads(json_str)
        self.assertIsInstance(parsed, dict)

    def test_abstract_methods_must_be_implemented(self) -> None:
        """
        Test that subclasses must implement abstract methods.

        Returns:
            None: This test does not return a value.
        """
        # This test verifies that ActionSchema cannot be instantiated without description()
        with self.assertRaises(TypeError):
            class IncompleteAction(ActionSchema):
                name: str = Field(description = "Test field")
                # Missing description() implementation

            # This should raise TypeError due to abstract method
            IncompleteAction(name = "test")

    def test_nested_action_schema_fields(self) -> None:
        """
        Test handling of nested ActionSchema fields.

        Returns:
            None: This test does not return a value.
        """
        class NestedAction(ActionSchema):
            nested_name: str = Field(description = "Nested name")

            @classmethod
            @override
            def description(cls) -> str:
                return "Nested action"

        class ParentAction(ActionSchema):
            parent_name: str = Field(description = "Parent name")
            nested: NestedAction = Field(description = "Nested action field")

            @classmethod
            @override
            def description(cls) -> str:
                return "Parent action"

        result = ParentAction.to_dict()

        self.assertIn("ParentAction", result)
        fields = result["ParentAction"]["fields"]

        # Check nested field structure
        nested_field = fields["nested"]
        self.assertEqual(nested_field["type"], "NestedAction")
        self.assertEqual(nested_field["description"], "Nested action")
        self.assertIn("fields", nested_field)

        # Check nested fields
        nested_fields = nested_field["fields"]
        self.assertIn("nested_name", nested_fields)

    def test_schema_creation_with_valid_data(self) -> None:
        """
        Test creating schema instances with valid data.

        Returns:
            None: This test does not return a value.
        """
        instance = self.test_action_class(name = "test", value = 100)

        # Type assertions to help the linter
        name = cast(str, instance.name)
        value = cast(int, instance.value)
        optional = cast(str | None, instance.optional)

        self.assertEqual(name, "test")
        self.assertEqual(value, 100)
        self.assertIsNone(optional)

    def test_schema_creation_with_defaults(self) -> None:
        """
        Test creating schema instances with default values.

        Returns:
            None: This test does not return a value.
        """
        instance = self.test_action_class(name = "test")

        # Type assertions to help the linter
        name = cast(str, instance.name)
        value = cast(int, instance.value)
        optional = cast(str | None, instance.optional)

        self.assertEqual(name, "test")
        self.assertEqual(value, 42)  # default value
        self.assertIsNone(optional)

    def test_schema_validation_errors(self) -> None:
        """
        Test that validation errors are raised for invalid data.

        Returns:
            None: This test does not return a value.
        """
        with self.assertRaises(ValidationError):
            self.test_action_class(name = "test", value = "not_an_int")

    def test_to_json_schema_consistency(self) -> None:
        """
        Test that to_dict and to_json_schema are consistent.

        Returns:
            None: This test does not return a value.
        """
        dict_result = self.test_action_class.to_dict()
        schema_result = self.test_action_class.model_json_schema()

        # Both should contain the same field information
        dict_fields = dict_result["TestAction"]["fields"]
        schema_properties = schema_result["properties"]

        for field_name in dict_fields:
            self.assertIn(field_name, schema_properties)


if __name__ == "__main__":
    from unittest import main
    main()
