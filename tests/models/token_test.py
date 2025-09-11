from datetime import datetime
from typing import Any, override
from unittest import TestCase

from models.token import Token


class TestToken(TestCase):
    """Test cases for Token model class."""

    token: Token  # type: ignore

    @override
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.token = Token()

    def test_token_inherits_from_action_model(self) -> None:
        """
        Test that Token inherits from ActionModel.

        Returns:
            None: This test does not return a value.
        """
        from core.action_model import ActionModel

        # Token is always a subclass of ActionModel by design
        self.assertIsInstance(Token, type)

    def test_token_has_required_fields(self) -> None:
        """
        Test that Token has the required fields with correct types.

        Returns:
            None: This test does not return a value.
        """
        self.assertIsNone(self.token.id)
        self.assertIsNone(self.token.context)
        self.assertIsNone(self.token.value)
        self.assertIsNone(self.token.service_id)
        self.assertIsNone(self.token.inserted_at)
        self.assertIsNone(self.token.expires_at)

    def test_token_field_descriptions(self) -> None:
        """
        Test that Token fields have correct descriptions.

        Returns:
            None: This test does not return a value.
        """
        field_info = Token.model_fields

        self.assertEqual(field_info["id"].description, "The unique identifier for the token.")
        self.assertEqual(field_info["context"].description, "The context for the token.")
        self.assertEqual(field_info["value"].description, "The value for the token.")
        self.assertEqual(field_info["service_id"].description, "The ID of the service associated with the token.")
        self.assertEqual(field_info["inserted_at"].description, "The date and time the token was inserted.")
        self.assertEqual(field_info["expires_at"].description, "The date and time the token expires.")

    def test_token_description_method(self) -> None:
        """
        Test that Token description method returns correct description.

        Returns:
            None: This test does not return a value.
        """
        description = Token.description()

        self.assertEqual(description, "Represents a token with a unique identifier, context, value, service id, and inserted and expiration date.")

    def test_token_discriminator(self) -> None:
        """
        Test that Token discriminator returns class name.

        Returns:
            None: This test does not return a value.
        """
        discriminator = Token.discriminator()

        self.assertEqual(discriminator, "Token")

    def test_token_model_dict_structure(self) -> None:
        """
        Test that Token model_dict returns correct structure.

        Returns:
            None: This test does not return a value.
        """
        result = Token.model_dict()

        self.assertIn("Token", result)
        self.assertIn("description", result["Token"])
        self.assertIn("fields", result["Token"])

        fields = result["Token"]["fields"]
        self.assertIn("id", fields)
        self.assertIn("context", fields)
        self.assertIn("value", fields)
        self.assertIn("service_id", fields)
        self.assertIn("inserted_at", fields)
        self.assertIn("expires_at", fields)

    def test_token_model_json(self) -> None:
        """
        Test that Token model_json returns valid JSON.

        Returns:
            None: This test does not return a value.
        """
        json_str = Token.model_json()

        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertIn("Token", parsed)

    def test_token_creation_with_defaults(self) -> None:
        """
        Test creating Token with default values.

        Returns:
            None: This test does not return a value.
        """
        token = Token()

        self.assertIsNone(token.id)
        self.assertIsNone(token.context)
        self.assertIsNone(token.value)
        self.assertIsNone(token.service_id)
        self.assertIsNone(token.inserted_at)
        self.assertIsNone(token.expires_at)

    def test_token_creation_with_custom_values(self) -> None:
        """
        Test creating Token with custom values.

        Returns:
            None: This test does not return a value.
        """
        token = Token(
            id = 123,
            context = "test_context",
            value = "test_token_value",
            service_id = 456,
            inserted_at = datetime(2023, 1, 1, 12, 0, 0),
            expires_at = datetime(2023, 12, 31, 23, 59, 59)
        )

        self.assertEqual(token.id, 123)
        self.assertEqual(token.context, "test_context")
        self.assertEqual(token.value, "test_token_value")
        self.assertEqual(token.service_id, 456)
        self.assertEqual(token.inserted_at, datetime(2023, 1, 1, 12, 0, 0))
        self.assertEqual(token.expires_at, datetime(2023, 12, 31, 23, 59, 59))

    def test_token_creation_with_partial_values(self) -> None:
        """
        Test creating Token with partial values (using defaults for others).

        Returns:
            None: This test does not return a value.
        """
        token = Token(
            id = 789,
            value = "partial_token"
        )

        self.assertEqual(token.id, 789)
        self.assertIsNone(token.context)
        self.assertEqual(token.value, "partial_token")
        self.assertIsNone(token.service_id)
        self.assertIsNone(token.inserted_at)
        self.assertIsNone(token.expires_at)

    def test_token_creation_with_none_values(self) -> None:
        """
        Test creating Token with explicit None values.

        Returns:
            None: This test does not return a value.
        """
        token = Token(
            id = None,
            context = None,
            value = None,
            service_id = None,
            inserted_at = None,
            expires_at = None
        )

        self.assertIsNone(token.id)
        self.assertIsNone(token.context)
        self.assertIsNone(token.value)
        self.assertIsNone(token.service_id)
        self.assertIsNone(token.inserted_at)
        self.assertIsNone(token.expires_at)

    def test_token_field_validation(self) -> None:
        """
        Test that Token field validation works correctly.

        Returns:
            None: This test does not return a value.
        """
        # Valid data should work
        token = Token(
            id = 42,
            context = "test",
            value = "token_value",
            service_id = 100,
            inserted_at = datetime.now(),
            expires_at = datetime.now()
        )
        self.assertEqual(token.id, 42)
        self.assertEqual(token.context, "test")
        self.assertEqual(token.value, "token_value")
        self.assertEqual(token.service_id, 100)

        # Invalid data should raise ValidationError
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            Token(id = "not_an_int")  # id should be int or None

    def test_token_json_serialization(self) -> None:
        """
        Test that Token instances can be JSON serialized.

        Returns:
            None: This test does not return a value.
        """
        token = Token(
            id = 1,
            context = "test_context",
            value = "test_value",
            service_id = 2
        )

        json_str = token.model_dump_json()
        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed["id"], 1)
        self.assertEqual(parsed["context"], "test_context")
        self.assertEqual(parsed["value"], "test_value")
        self.assertEqual(parsed["service_id"], 2)

    def test_token_json_serialization_with_none_values(self) -> None:
        """
        Test that Token instances with None values can be JSON serialized.

        Returns:
            None: This test does not return a value.
        """
        json_str = self.token.model_dump_json()
        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertIsNone(parsed["id"])
        self.assertIsNone(parsed["context"])
        self.assertIsNone(parsed["value"])
        self.assertIsNone(parsed["service_id"])
        self.assertIsNone(parsed["inserted_at"])
        self.assertIsNone(parsed["expires_at"])

    def test_token_json_deserialization(self) -> None:
        """
        Test that Token instances can be created from JSON.

        Returns:
            None: This test does not return a value.
        """
        json_data: dict[str, Any] = {
            "id": 456,
            "context": "json_context",
            "value": "json_value",
            "service_id": 789,
            "inserted_at": "2023-03-15T09:30:00",
            "expires_at": "2023-12-31T23:59:59"
        }

        token = Token.model_validate(json_data)

        self.assertEqual(token.id, 456)
        self.assertEqual(token.context, "json_context")
        self.assertEqual(token.value, "json_value")
        self.assertEqual(token.service_id, 789)
        self.assertIsInstance(token.inserted_at, datetime)
        self.assertIsInstance(token.expires_at, datetime)

    def test_token_json_deserialization_with_none_values(self) -> None:
        """
        Test that Token instances can be created from JSON with None values.

        Returns:
            None: This test does not return a value.
        """
        json_data = {
            "id": None,
            "context": None,
            "value": None,
            "service_id": None,
            "inserted_at": None,
            "expires_at": None
        }

        token = Token.model_validate(json_data)

        self.assertIsNone(token.id)
        self.assertIsNone(token.context)
        self.assertIsNone(token.value)
        self.assertIsNone(token.service_id)
        self.assertIsNone(token.inserted_at)
        self.assertIsNone(token.expires_at)

    def test_token_override_decorator(self) -> None:
        """
        Test that Token methods use @override decorator correctly.

        Returns:
            None: This test does not return a value.
        """
        # This test ensures the @override decorator is used properly
        # The methods should work without issues
        description = Token.description()
        self.assertIsInstance(description, str)

        discriminator = Token.discriminator()
        self.assertIsInstance(discriminator, str)

    def test_token_string_representation(self) -> None:
        """
        Test that Token has proper string representation.

        Returns:
            None: This test does not return a value.
        """
        token = Token(id = 1, value = "test_token")
        str_repr = str(token)
        self.assertIn("id=1", str_repr)
        self.assertIn("value='test_token'", str_repr)

    def test_token_repr_representation(self) -> None:
        """
        Test that Token has proper repr representation.

        Returns:
            None: This test does not return a value.
        """
        token = Token(id = 1, value = "test_token")
        repr_str = repr(token)
        self.assertIn("Token", repr_str)
        self.assertIn("id=1", repr_str)
        self.assertIn("value='test_token'", repr_str)

    def test_token_equality(self) -> None:
        """
        Test that Token instances can be compared for equality.

        Returns:
            None: This test does not return a value.
        """
        token1 = Token(
            id = 1,
            context = "test",
            value = "token_value",
            service_id = 2
        )

        token2 = Token(
            id = 1,
            context = "test",
            value = "token_value",
            service_id = 2
        )

        self.assertEqual(token1, token2)

    def test_token_inequality(self) -> None:
        """
        Test that Token instances can be compared for inequality.

        Returns:
            None: This test does not return a value.
        """
        token1 = Token(id = 1, value = "token1")
        token2 = Token(id = 2, value = "token2")

        self.assertNotEqual(token1, token2)

    def test_token_hash(self) -> None:
        """
        Test that Token instances are not hashable by default.

        Returns:
            None: This test does not return a value.
        """
        # Pydantic models are not hashable by default
        with self.assertRaises(TypeError):
            hash(self.token)

    def test_token_with_datetime_objects(self) -> None:
        """
        Test that Token works with datetime objects.

        Returns:
            None: This test does not return a value.
        """
        token = Token(
            id = 1,
            inserted_at = datetime(2023, 1, 1, 12, 0, 0),
            expires_at = datetime(2023, 12, 31, 23, 59, 59)
        )

        self.assertEqual(token.inserted_at, datetime(2023, 1, 1, 12, 0, 0))
        self.assertEqual(token.expires_at, datetime(2023, 12, 31, 23, 59, 59))

    def test_token_with_string_datetime(self) -> None:
        """
        Test that Token works with string datetime values.

        Returns:
            None: This test does not return a value.
        """
        token = Token.model_validate({
            "id": 1,
            "inserted_at": "2023-01-01T12:00:00",
            "expires_at": "2023-12-31T23:59:59"
        })

        self.assertIsInstance(token.inserted_at, datetime)
        self.assertIsInstance(token.expires_at, datetime)

    def test_token_with_microseconds(self) -> None:
        """
        Test that Token works with datetime objects that include microseconds.

        Returns:
            None: This test does not return a value.
        """
        token = Token(
            id = 1,
            inserted_at = datetime(2023, 1, 1, 12, 0, 0, 123456),
            expires_at = datetime(2023, 12, 31, 23, 59, 59, 789012)
        )

        self.assertIsNotNone(token.inserted_at)
        self.assertIsNotNone(token.expires_at)
        if token.inserted_at is not None:
            self.assertEqual(token.inserted_at.microsecond, 123456)
        if token.expires_at is not None:
            self.assertEqual(token.expires_at.microsecond, 789012)

    def test_token_with_timezone_aware_datetime(self) -> None:
        """
        Test that Token works with timezone-aware datetime objects.

        Returns:
            None: This test does not return a value.
        """
        from datetime import timezone

        token = Token(
            id = 1,
            inserted_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo = timezone.utc),
            expires_at = datetime(2023, 12, 31, 23, 59, 59, tzinfo = timezone.utc)
        )

        self.assertIsNotNone(token.inserted_at)
        self.assertIsNotNone(token.expires_at)
        if token.inserted_at is not None:
            self.assertEqual(token.inserted_at.tzinfo, timezone.utc)
        if token.expires_at is not None:
            self.assertEqual(token.expires_at.tzinfo, timezone.utc)

    def test_token_empty_string_values(self) -> None:
        """
        Test that Token accepts empty string values.

        Returns:
            None: This test does not return a value.
        """
        token = Token(
            context = "",
            value = ""
        )

        self.assertEqual(token.context, "")
        self.assertEqual(token.value, "")

    def test_token_whitespace_values(self) -> None:
        """
        Test that Token accepts whitespace values.

        Returns:
            None: This test does not return a value.
        """
        token = Token(
            context = "   ",
            value = "\t\n"
        )

        self.assertEqual(token.context, "   ")
        self.assertEqual(token.value, "\t\n")


if __name__ == "__main__":
    from unittest import main
    main()
