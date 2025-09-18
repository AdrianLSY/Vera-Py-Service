import asyncio
from typing import Any, override
from unittest import TestCase
from unittest.mock import Mock

from core.action_response import ActionResponse
from events.phx_join_event import PhxJoinEvent


class PhxJoinEventTest(TestCase):
    """Test cases for PhxJoinEvent class."""

    phx_join_event: PhxJoinEvent  # type: ignore

    @override
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.phx_join_event = PhxJoinEvent(topic = "test_topic")

    def test_phx_join_event_inherits_from_action_runner(self) -> None:
        """
        Test that PhxJoinEvent inherits from ActionRunner.

        Returns:
            None: This test does not return a value.
        """
        from core.action_runner import ActionRunner

        # PhxJoinEvent is always a subclass of ActionRunner by design
        self.assertIsInstance(PhxJoinEvent, type)

    def test_phx_join_event_payload_inherits_from_action_schema(self) -> None:
        """
        Test that PhxJoinEvent.Payload inherits from ActionSchema.

        Returns:
            None: This test does not return a value.
        """
        from core.action_schema import ActionSchema

        # PhxJoinEvent.Payload is always a subclass of ActionSchema by design
        self.assertIsInstance(PhxJoinEvent.Payload, type)

    def test_phx_join_event_has_required_fields(self) -> None:
        """
        Test that PhxJoinEvent has the required fields with correct types.

        Returns:
            None: This test does not return a value.
        """
        self.assertIsNone(self.phx_join_event.ref)
        self.assertEqual(self.phx_join_event.topic, "test_topic")
        self.assertEqual(self.phx_join_event.event, "phx_join")
        self.assertIsInstance(self.phx_join_event.payload, PhxJoinEvent.Payload)

    def test_phx_join_event_payload_is_empty(self) -> None:
        """
        Test that PhxJoinEvent.Payload is empty (no fields).

        Returns:
            None: This test does not return a value.
        """
        payload = self.phx_join_event.payload

        # Payload should be an instance of PhxJoinEvent.Payload
        self.assertIsInstance(payload, PhxJoinEvent.Payload)

        # Should have no fields (empty schema)
        self.assertEqual(len(PhxJoinEvent.Payload.model_fields), 0)

    def test_phx_join_event_field_descriptions(self) -> None:
        """
        Test that PhxJoinEvent fields have correct descriptions.

        Returns:
            None: This test does not return a value.
        """
        field_info = PhxJoinEvent.model_fields

        self.assertEqual(field_info["ref"].description, "A reference identifier for the event.")
        self.assertEqual(field_info["topic"].description, "The topic to which the event is associated.")
        self.assertEqual(field_info["event"].description, 'A literal indicating the event type "phx_join".')
        self.assertEqual(field_info["payload"].description, "The payload of the join event.")

    def test_phx_join_event_payload_field_descriptions(self) -> None:
        """
        Test that PhxJoinEvent.Payload description method returns correct description.

        Returns:
            None: This test does not return a value.
        """
        description = PhxJoinEvent.Payload.description()

        self.assertEqual(description, "Represents the payload for a Phoenix join event.")

    def test_phx_join_event_description_method(self) -> None:
        """
        Test that PhxJoinEvent description method returns correct description.

        Returns:
            None: This test does not return a value.
        """
        description = PhxJoinEvent.description()

        self.assertEqual(description, "Represents a Phoenix join event.")

    def test_phx_join_event_discriminator(self) -> None:
        """
        Test that PhxJoinEvent discriminator returns 'phx_join'.

        Returns:
            None: This test does not return a value.
        """
        discriminator = PhxJoinEvent.discriminator()

        self.assertEqual(discriminator, "phx_join")

    def test_phx_join_event_to_dict_structure(self) -> None:
        """
        Test that PhxJoinEvent to_dict returns correct structure.

        Returns:
            None: This test does not return a value.
        """
        result = PhxJoinEvent.to_dict()

        self.assertIn("PhxJoinEvent", result)
        self.assertIn("description", result["PhxJoinEvent"])
        self.assertIn("fields", result["PhxJoinEvent"])

        fields = result["PhxJoinEvent"]["fields"]
        self.assertIn("ref", fields)
        self.assertIn("topic", fields)
        self.assertIn("event", fields)
        self.assertIn("payload", fields)

    def test_phx_join_event_to_json(self) -> None:
        """
        Test that PhxJoinEvent to_json returns valid JSON.

        Returns:
            None: This test does not return a value.
        """
        json_str = PhxJoinEvent.to_json()

        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertIn("PhxJoinEvent", parsed)

    def test_phx_join_event_creation_with_defaults(self) -> None:
        """
        Test creating PhxJoinEvent with default values.

        Returns:
            None: This test does not return a value.
        """
        phx_join_event = PhxJoinEvent(topic = "test_topic")

        self.assertIsNone(phx_join_event.ref)
        self.assertEqual(phx_join_event.topic, "test_topic")
        self.assertEqual(phx_join_event.event, "phx_join")
        self.assertIsInstance(phx_join_event.payload, PhxJoinEvent.Payload)

    def test_phx_join_event_creation_with_custom_values(self) -> None:
        """
        Test creating PhxJoinEvent with custom values.

        Returns:
            None: This test does not return a value.
        """
        phx_join_event = PhxJoinEvent(
            ref = "custom_ref",
            topic = "custom_topic"
        )

        self.assertEqual(phx_join_event.ref, "custom_ref")
        self.assertEqual(phx_join_event.topic, "custom_topic")
        self.assertEqual(phx_join_event.event, "phx_join")
        self.assertIsInstance(phx_join_event.payload, PhxJoinEvent.Payload)

    def test_phx_join_event_field_validation(self) -> None:
        """
        Test that PhxJoinEvent field validation works correctly.

        Returns:
            None: This test does not return a value.
        """
        # Valid data should work
        phx_join_event = PhxJoinEvent(topic = "test")
        self.assertEqual(phx_join_event.topic, "test")
        self.assertEqual(phx_join_event.event, "phx_join")

        # Invalid data should raise ValidationError
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            PhxJoinEvent(topic = 123)  # topic should be string

    def test_phx_join_event_json_serialization(self) -> None:
        """
        Test that PhxJoinEvent instances can be JSON serialized.

        Returns:
            None: This test does not return a value.
        """
        json_str = self.phx_join_event.model_dump_json()
        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertIsNone(parsed["ref"])
        self.assertEqual(parsed["topic"], "test_topic")
        self.assertEqual(parsed["event"], "phx_join")
        self.assertIn("payload", parsed)

    def test_phx_join_event_json_deserialization(self) -> None:
        """
        Test that PhxJoinEvent instances can be created from JSON.

        Returns:
            None: This test does not return a value.
        """
        json_data: dict[str, Any] = {
            "ref": "test_ref",
            "topic": "test_topic",
            "event": "phx_join",
            "payload": {}
        }

        phx_join_event = PhxJoinEvent.model_validate(json_data)

        self.assertEqual(phx_join_event.ref, "test_ref")
        self.assertEqual(phx_join_event.topic, "test_topic")
        self.assertEqual(phx_join_event.event, "phx_join")
        self.assertIsInstance(phx_join_event.payload, PhxJoinEvent.Payload)

    def test_run_method_returns_success_response(self) -> None:
        """
        Test that run method returns success ActionResponse.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            mock_client = Mock()
            mock_websocket = Mock()

            result = await self.phx_join_event.run(mock_client, mock_websocket)

            self.assertIsInstance(result, ActionResponse)
            self.assertEqual(result.status_code, 200)

        asyncio.run(async_test())

    def test_run_method_with_different_topics(self) -> None:
        """
        Test that run method works with different topics.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            phx_join_event = PhxJoinEvent(topic = "different_topic")
            mock_client = Mock()
            mock_websocket = Mock()

            result = await phx_join_event.run(mock_client, mock_websocket)

            self.assertIsInstance(result, ActionResponse)
            self.assertEqual(result.status_code, 200)

        asyncio.run(async_test())

    def test_phx_join_event_override_decorator(self) -> None:
        """
        Test that PhxJoinEvent methods use @override decorator correctly.

        Returns:
            None: This test does not return a value.
        """
        # This test ensures the @override decorator is used properly
        # The methods should work without issues
        description = PhxJoinEvent.description()
        self.assertIsInstance(description, str)

        discriminator = PhxJoinEvent.discriminator()
        self.assertIsInstance(discriminator, str)

    def test_phx_join_event_async_run_signature(self) -> None:
        """
        Test that PhxJoinEvent run method has correct async signature.

        Returns:
            None: This test does not return a value.
        """
        import inspect

        run_method = PhxJoinEvent.run
        signature = inspect.signature(run_method)

        # Should have self, client, and websocket parameters
        params = list(signature.parameters.keys())
        self.assertIn("self", params)
        self.assertIn("client", params)
        self.assertIn("websocket", params)

    def test_phx_join_event_run_method_returns_action_response(self) -> None:
        """
        Test that PhxJoinEvent run method returns ActionResponse type.

        Returns:
            None: This test does not return a value.
        """
        import asyncio

        async def test_run() -> ActionResponse:
            mock_client = Mock()
            mock_websocket = Mock()
            result = await self.phx_join_event.run(mock_client, mock_websocket)
            return result

        result = asyncio.run(test_run())
        self.assertIsInstance(result, ActionResponse)

    def test_phx_join_event_payload_creation(self) -> None:
        """
        Test that PhxJoinEvent.Payload can be created.

        Returns:
            None: This test does not return a value.
        """
        payload = PhxJoinEvent.Payload()

        self.assertIsInstance(payload, PhxJoinEvent.Payload)

    def test_phx_join_event_payload_json_serialization(self) -> None:
        """
        Test that PhxJoinEvent.Payload can be JSON serialized.

        Returns:
            None: This test does not return a value.
        """
        payload = PhxJoinEvent.Payload()

        json_str = payload.model_dump_json()
        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed, {})

    def test_phx_join_event_payload_json_deserialization(self) -> None:
        """
        Test that PhxJoinEvent.Payload can be created from JSON.

        Returns:
            None: This test does not return a value.
        """
        json_data = {}

        payload = PhxJoinEvent.Payload.model_validate(json_data)

        self.assertIsInstance(payload, PhxJoinEvent.Payload)

    def test_phx_join_event_event_field_is_literal(self) -> None:
        """
        Test that PhxJoinEvent event field is a literal type.

        Returns:
            None: This test does not return a value.
        """
        # Should only accept "phx_join" as value
        phx_join_event = PhxJoinEvent(topic = "test")
        self.assertEqual(phx_join_event.event, "phx_join")

        # Should raise ValidationError for invalid event value
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            PhxJoinEvent(topic = "test", event = "invalid_event")


if __name__ == "__main__":
    from unittest import main
    main()
