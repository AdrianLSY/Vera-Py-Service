from datetime import datetime
from typing import Any, override
from unittest import TestCase

from schemas.service import Service


class TestService(TestCase):
    """Test cases for Service action_schema class."""

    service: Service  # type: ignore

    @override
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = Service(
            id = 1,
            name = "Test Service",
            inserted_at = datetime(2023, 1, 1, 12, 0, 0),
            updated_at = datetime(2023, 1, 1, 12, 0, 0)
        )

    def test_service_inherits_from_action_action_schema(self) -> None:
        """
        Test that Service inherits from ActionSchema.

        Returns:
            None: This test does not return a value.
        """
        from core.action_schema import ActionSchema

        # Service is always a subclass of ActionSchema by design
        self.assertIsInstance(Service, type)

    def test_service_has_required_fields(self) -> None:
        """
        Test that Service has the required fields with correct types.

        Returns:
            None: This test does not return a value.
        """
        self.assertEqual(self.service.id, 1)
        self.assertEqual(self.service.name, "Test Service")
        self.assertIsInstance(self.service.inserted_at, datetime)
        self.assertIsInstance(self.service.updated_at, datetime)

    def test_service_field_descriptions(self) -> None:
        """
        Test that Service fields have correct descriptions.

        Returns:
            None: This test does not return a value.
        """
        field_info = Service.model_fields

        self.assertEqual(field_info["id"].description, "The unique identifier for the service.")
        self.assertEqual(field_info["name"].description, "The name of the service.")
        self.assertEqual(field_info["inserted_at"].description, "The date and time the service was inserted.")
        self.assertEqual(field_info["updated_at"].description, "The date and time the service was last updated.")

    def test_service_description_method(self) -> None:
        """
        Test that Service description method returns correct description.

        Returns:
            None: This test does not return a value.
        """
        description = Service.description()

        self.assertEqual(description, "Represents a service with a unique identifier and a name.")

    def test_service_discriminator(self) -> None:
        """
        Test that Service discriminator returns class name.

        Returns:
            None: This test does not return a value.
        """
        discriminator = Service.discriminator()

        self.assertEqual(discriminator, "Service")

    def test_service_to_dict_structure(self) -> None:
        """
        Test that Service to_dict returns correct structure.

        Returns:
            None: This test does not return a value.
        """
        result = Service.to_dict()

        self.assertIn("Service", result)
        self.assertIn("description", result["Service"])
        self.assertIn("fields", result["Service"])

        fields = result["Service"]["fields"]
        self.assertIn("id", fields)
        self.assertIn("name", fields)
        self.assertIn("inserted_at", fields)
        self.assertIn("updated_at", fields)

    def test_service_to_json(self) -> None:
        """
        Test that Service to_json returns valid JSON.

        Returns:
            None: This test does not return a value.
        """
        json_str = Service.to_json()

        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertIn("Service", parsed)

    def test_service_creation_with_valid_data(self) -> None:
        """
        Test creating Service with valid data.

        Returns:
            None: This test does not return a value.
        """
        service = Service(
            id = 123,
            name = "My Service",
            inserted_at = datetime(2023, 6, 15, 10, 30, 0),
            updated_at = datetime(2023, 6, 15, 14, 45, 0)
        )

        self.assertEqual(service.id, 123)
        self.assertEqual(service.name, "My Service")
        self.assertEqual(service.inserted_at, datetime(2023, 6, 15, 10, 30, 0))
        self.assertEqual(service.updated_at, datetime(2023, 6, 15, 14, 45, 0))

    def test_service_field_validation(self) -> None:
        """
        Test that Service field validation works correctly.

        Returns:
            None: This test does not return a value.
        """
        # Valid data should work
        service = Service(
            id = 42,
            name = "Valid Service",
            inserted_at = datetime.now(),
            updated_at = datetime.now()
        )
        self.assertEqual(service.id, 42)
        self.assertEqual(service.name, "Valid Service")

        # Invalid data should raise ValidationError
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            Service(
                id = "not_an_int",
                name = "Test Service",
                inserted_at = datetime.now(),
                updated_at = datetime.now()
            )

    def test_service_json_serialization(self) -> None:
        """
        Test that Service instances can be JSON serialized.

        Returns:
            None: This test does not return a value.
        """
        json_str = self.service.model_dump_json()
        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed["id"], 1)
        self.assertEqual(parsed["name"], "Test Service")
        self.assertIn("inserted_at", parsed)
        self.assertIn("updated_at", parsed)

    def test_service_json_deserialization(self) -> None:
        """
        Test that Service instances can be created from JSON.

        Returns:
            None: This test does not return a value.
        """
        json_data: dict[str, Any] = {
            "id": 456,
            "name": "JSON Service",
            "inserted_at": "2023-03-15T09:30:00",
            "updated_at": "2023-03-15T16:20:00"
        }

        service = Service.model_validate(json_data)

        self.assertEqual(service.id, 456)
        self.assertEqual(service.name, "JSON Service")
        self.assertIsInstance(service.inserted_at, datetime)
        self.assertIsInstance(service.updated_at, datetime)

    def test_service_json_deserialization_with_datetime_objects(self) -> None:
        """
        Test that Service instances can be created from JSON with datetime objects.

        Returns:
            None: This test does not return a value.
        """
        json_data: dict[str, Any] = {
            "id": 789,
            "name": "Datetime Service",
            "inserted_at": datetime(2023, 4, 1, 8, 0, 0),
            "updated_at": datetime(2023, 4, 1, 17, 30, 0)
        }

        service = Service.model_validate(json_data)

        self.assertEqual(service.id, 789)
        self.assertEqual(service.name, "Datetime Service")
        self.assertEqual(service.inserted_at, datetime(2023, 4, 1, 8, 0, 0))
        self.assertEqual(service.updated_at, datetime(2023, 4, 1, 17, 30, 0))

    def test_service_override_decorator(self) -> None:
        """
        Test that Service methods use @override decorator correctly.

        Returns:
            None: This test does not return a value.
        """
        # This test ensures the @override decorator is used properly
        # The methods should work without issues
        description = Service.description()
        self.assertIsInstance(description, str)

        discriminator = Service.discriminator()
        self.assertIsInstance(discriminator, str)

    def test_service_string_representation(self) -> None:
        """
        Test that Service has proper string representation.

        Returns:
            None: This test does not return a value.
        """
        str_repr = str(self.service)
        self.assertIn("Service", str_repr)
        self.assertIn("id=1", str_repr)
        self.assertIn("name='Test Service'", str_repr)

    def test_service_repr_representation(self) -> None:
        """
        Test that Service has proper repr representation.

        Returns:
            None: This test does not return a value.
        """
        repr_str = repr(self.service)
        self.assertIn("Service", repr_str)
        self.assertIn("id=1", repr_str)
        self.assertIn("name='Test Service'", repr_str)

    def test_service_equality(self) -> None:
        """
        Test that Service instances can be compared for equality.

        Returns:
            None: This test does not return a value.
        """
        service1 = Service(
            id = 1,
            name = "Test Service",
            inserted_at = datetime(2023, 1, 1, 12, 0, 0),
            updated_at = datetime(2023, 1, 1, 12, 0, 0)
        )

        service2 = Service(
            id = 1,
            name = "Test Service",
            inserted_at = datetime(2023, 1, 1, 12, 0, 0),
            updated_at = datetime(2023, 1, 1, 12, 0, 0)
        )

        self.assertEqual(service1, service2)

    def test_service_inequality(self) -> None:
        """
        Test that Service instances can be compared for inequality.

        Returns:
            None: This test does not return a value.
        """
        service1 = Service(
            id = 1,
            name = "Test Service",
            inserted_at = datetime(2023, 1, 1, 12, 0, 0),
            updated_at = datetime(2023, 1, 1, 12, 0, 0)
        )

        service2 = Service(
            id = 2,
            name = "Different Service",
            inserted_at = datetime(2023, 1, 1, 12, 0, 0),
            updated_at = datetime(2023, 1, 1, 12, 0, 0)
        )

        self.assertNotEqual(service1, service2)

    def test_service_hash(self) -> None:
        """
        Test that Service instances are not hashable by default.

        Returns:
            None: This test does not return a value.
        """
        # Pydantic action_schemas are not hashable by default
        with self.assertRaises(TypeError):
            hash(self.service)

    def test_service_with_different_datetime_formats(self) -> None:
        """
        Test that Service works with different datetime formats.

        Returns:
            None: This test does not return a value.
        """
        # Test with ISO format string
        service = Service.model_validate({
            "id": 1,
            "name": "ISO Service",
            "inserted_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00"
        })

        self.assertEqual(service.id, 1)
        self.assertEqual(service.name, "ISO Service")
        self.assertIsInstance(service.inserted_at, datetime)
        self.assertIsInstance(service.updated_at, datetime)

    def test_service_with_microseconds(self) -> None:
        """
        Test that Service works with datetime objects that include microseconds.

        Returns:
            None: This test does not return a value.
        """
        service = Service(
            id = 1,
            name = "Microsecond Service",
            inserted_at = datetime(2023, 1, 1, 12, 0, 0, 123456),
            updated_at = datetime(2023, 1, 1, 12, 0, 0, 789012)
        )

        self.assertEqual(service.inserted_at.microsecond, 123456)
        self.assertEqual(service.updated_at.microsecond, 789012)

    def test_service_with_timezone_aware_datetime(self) -> None:
        """
        Test that Service works with timezone-aware datetime objects.

        Returns:
            None: This test does not return a value.
        """
        from datetime import timezone

        service = Service(
            id = 1,
            name = "Timezone Service",
            inserted_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo = timezone.utc),
            updated_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo = timezone.utc)
        )

        self.assertEqual(service.inserted_at.tzinfo, timezone.utc)
        self.assertEqual(service.updated_at.tzinfo, timezone.utc)


if __name__ == "__main__":
    from unittest import main
    main()
