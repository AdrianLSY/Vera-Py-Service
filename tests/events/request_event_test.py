import asyncio
from typing import Any, override
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from core.action_response import ActionResponse
from events.request_event import RequestEvent


class RequestEventTest(TestCase):
    """Test cases for RequestEvent class."""

    payload: RequestEvent.Payload  # type: ignore
    request_event: RequestEvent  # type: ignore

    @override
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.payload = RequestEvent.Payload(
            action = "test_action",
            fields = {"key": "value"},
            response_ref = "test_ref"
        )
        self.request_event = RequestEvent(
            ref = "test_ref",
            topic = "test_topic",
            payload = self.payload
        )

    def test_request_event_has_required_fields(self) -> None:
        """
        Test that RequestEvent has the required fields with correct types.

        Returns:
            None: This test does not return a value.
        """
        self.assertEqual(self.request_event.ref, "test_ref")
        self.assertEqual(self.request_event.topic, "test_topic")
        self.assertEqual(self.request_event.event, "request")
        self.assertIsInstance(self.request_event.payload, RequestEvent.Payload)

    def test_request_event_payload_has_required_fields(self) -> None:
        """
        Test that RequestEvent.Payload has the required fields.

        Returns:
            None: This test does not return a value.
        """
        self.assertEqual(self.payload.action, "test_action")
        self.assertEqual(self.payload.fields, {"key": "value"})
        self.assertEqual(self.payload.response_ref, "test_ref")

    def test_request_event_field_descriptions(self) -> None:
        """
        Test that RequestEvent fields have correct descriptions.

        Returns:
            None: This test does not return a value.
        """
        field_info = RequestEvent.model_fields

        self.assertEqual(field_info["ref"].description, "A reference identifier for the event.")
        self.assertEqual(field_info["topic"].description, "The topic to which the event is associated.")
        self.assertEqual(field_info["event"].description, 'A literal indicating the event type "request".')
        self.assertEqual(field_info["payload"].description, "The payload containing the request information.")

    def test_request_event_payload_field_descriptions(self) -> None:
        """
        Test that RequestEvent.Payload fields have correct descriptions.

        Returns:
            None: This test does not return a value.
        """
        field_info = RequestEvent.Payload.model_fields

        self.assertEqual(field_info["action"].description, "The name of the action to run.")
        self.assertEqual(field_info["fields"].description, "The fields to pass to the action.")
        self.assertEqual(field_info["response_ref"].description, "The reference to send a response for the request.")

    def test_request_event_description_method(self) -> None:
        """
        Test that RequestEvent description method returns correct description.

        Returns:
            None: This test does not return a value.
        """
        description = RequestEvent.description()

        self.assertEqual(description, "Represents a request event to be be handled by the corresponding action runner.")

    def test_request_event_payload_description_method(self) -> None:
        """
        Test that RequestEvent.Payload description method returns correct description.

        Returns:
            None: This test does not return a value.
        """
        description = RequestEvent.Payload.description()

        self.assertEqual(description, "Represents the payload for a request event.")

    def test_request_event_discriminator(self) -> None:
        """
        Test that RequestEvent discriminator returns 'request'.

        Returns:
            None: This test does not return a value.
        """
        discriminator = RequestEvent.discriminator()

        self.assertEqual(discriminator, "request")

    def test_request_event_to_dict_structure(self) -> None:
        """
        Test that RequestEvent to_dict returns correct structure.

        Returns:
            None: This test does not return a value.
        """
        result = RequestEvent.to_dict()

        self.assertIn("RequestEvent", result)
        self.assertIn("description", result["RequestEvent"])
        self.assertIn("fields", result["RequestEvent"])

        fields = result["RequestEvent"]["fields"]
        self.assertIn("ref", fields)
        self.assertIn("topic", fields)
        self.assertIn("event", fields)
        self.assertIn("payload", fields)

    def test_request_event_to_json(self) -> None:
        """
        Test that RequestEvent to_json returns valid JSON.

        Returns:
            None: This test does not return a value.
        """
        json_str = RequestEvent.to_json()

        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertIn("RequestEvent", parsed)

    def test_request_event_creation_with_defaults(self) -> None:
        """
        Test creating RequestEvent with default values.

        Returns:
            None: This test does not return a value.
        """
        payload = RequestEvent.Payload(
            action = "test_action",
            fields = {}
        )
        request_event = RequestEvent(
            topic = "test_topic",
            payload = payload
        )

        self.assertIsNone(request_event.ref)
        self.assertEqual(request_event.topic, "test_topic")
        self.assertEqual(request_event.event, "request")
        self.assertEqual(request_event.payload, payload)

    def test_request_event_payload_creation_with_defaults(self) -> None:
        """
        Test creating RequestEvent.Payload with default values.

        Returns:
            None: This test does not return a value.
        """
        payload = RequestEvent.Payload(
            action = "test_action",
            fields = {}
        )

        self.assertEqual(payload.action, "test_action")
        self.assertEqual(payload.fields, {})
        self.assertIsNone(payload.response_ref)

    def test_request_event_creation_with_custom_values(self) -> None:
        """
        Test creating RequestEvent with custom values.

        Returns:
            None: This test does not return a value.
        """
        payload = RequestEvent.Payload(
            action = "custom_action",
            fields = {"custom": "data"},
            response_ref = "custom_ref"
        )
        request_event = RequestEvent(
            ref = "custom_ref",
            topic = "custom_topic",
            payload = payload
        )

        self.assertEqual(request_event.ref, "custom_ref")
        self.assertEqual(request_event.topic, "custom_topic")
        self.assertEqual(request_event.event, "request")
        self.assertEqual(request_event.payload, payload)

    def test_request_event_field_validation(self) -> None:
        """
        Test that RequestEvent field validation works correctly.

        Returns:
            None: This test does not return a value.
        """
        # Valid data should work
        payload = RequestEvent.Payload(
            action = "test",
            fields = {}
        )
        request_event = RequestEvent(
            topic = "test",
            payload = payload
        )
        self.assertEqual(request_event.topic, "test")
        self.assertEqual(request_event.payload, payload)

        # Invalid data should raise ValidationError
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            RequestEvent(topic = 123, payload = payload)  # topic should be string

    def test_request_event_payload_field_validation(self) -> None:
        """
        Test that RequestEvent.Payload field validation works correctly.

        Returns:
            None: This test does not return a value.
        """
        # Valid data should work
        payload = RequestEvent.Payload(
            action = "test",
            fields = {"key": "value"}
        )
        self.assertEqual(payload.action, "test")
        self.assertEqual(payload.fields, {"key": "value"})

        # Invalid data should raise ValidationError
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            RequestEvent.Payload(action = 123, fields = {})  # action should be string

    def test_request_event_json_serialization(self) -> None:
        """
        Test that RequestEvent instances can be JSON serialized.

        Returns:
            None: This test does not return a value.
        """
        json_str = self.request_event.model_dump_json()
        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed["ref"], "test_ref")
        self.assertEqual(parsed["topic"], "test_topic")
        self.assertEqual(parsed["event"], "request")
        self.assertIn("payload", parsed)

    def test_request_event_json_deserialization(self) -> None:
        """
        Test that RequestEvent instances can be created from JSON.

        Returns:
            None: This test does not return a value.
        """
        json_data: dict[str, Any] = {
            "ref": "test_ref",
            "topic": "test_topic",
            "event": "request",
            "payload": {
                "action": "test_action",
                "fields": {"key": "value"},
                "response_ref": "test_ref"
            }
        }

        request_event = RequestEvent.model_validate(json_data)

        self.assertEqual(request_event.ref, "test_ref")
        self.assertEqual(request_event.topic, "test_topic")
        self.assertEqual(request_event.event, "request")
        self.assertEqual(request_event.payload.action, "test_action")
        self.assertEqual(request_event.payload.fields, {"key": "value"})
        self.assertEqual(request_event.payload.response_ref, "test_ref")

    @patch('events.request_event.dumps')
    def test_run_method_with_valid_action(self, mock_dumps: Mock) -> None:
        """
        Test that run method handles valid action correctly.

        Parameters:
            mock_dumps (Mock): Mock for the dumps function.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            mock_client = Mock()
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()

            # Mock the action in client.actions
            mock_action_class = Mock()
            mock_action_instance = Mock()
            mock_action_instance.run = AsyncMock(
                return_value = ActionResponse(
                    status_code = 200,
                    message = "Success"
                )
            )
            mock_action_class.return_value = mock_action_instance
            mock_client.actions = {"test_action": mock_action_class}

            # Mock dumps to return a JSON string
            mock_dumps.return_value = '{"response": "data"}'

            result = await self.request_event.run(mock_client, mock_websocket)

            # Should call the action
            mock_action_instance.run.assert_called_once_with(mock_client, mock_websocket)

            # Should send response via websocket
            mock_websocket.send.assert_called_once()

            # Should return the action response
            self.assertIsInstance(result, ActionResponse)
            self.assertEqual(result.status_code, 200)

        asyncio.run(async_test())

    @patch('events.request_event.dumps')
    def test_run_method_with_unknown_action(self, mock_dumps: Mock) -> None:
        """
        Test that run method handles unknown action correctly.

        Parameters:
            mock_dumps (Mock): Mock for the dumps function.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            mock_client = Mock()
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()

            # Mock empty actions dictionary
            mock_client.actions = {}

            # Mock dumps to return a JSON string
            mock_dumps.return_value = '{"response": "data"}'

            result = await self.request_event.run(mock_client, mock_websocket)

            # Should send error response via websocket
            mock_websocket.send.assert_called_once()

            # Should return error action response
            self.assertIsInstance(result, ActionResponse)
            self.assertEqual(result.status_code, 404)
            self.assertEqual(result.message, "Unknown action: test_action")

        asyncio.run(async_test())

    @patch('events.request_event.dumps')
    def test_run_method_with_action_exception(self, mock_dumps: Mock) -> None:
        """
        Test that run method handles action exception correctly.

        Parameters:
            mock_dumps (Mock): Mock for the dumps function.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            mock_client = Mock()
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()

            # Mock the action in client.actions to raise an exception
            mock_action = Mock()
            mock_action.run = AsyncMock(side_effect = Exception("Test error"))
            mock_client.actions = {"test_action": mock_action}

            # Mock dumps to return a JSON string
            mock_dumps.return_value = '{"response": "data"}'

            result = await self.request_event.run(mock_client, mock_websocket)

            # Should send error response via websocket
            mock_websocket.send.assert_called_once()

            # Should return error action response
            self.assertIsInstance(result, ActionResponse)
            self.assertEqual(result.status_code, 500)
            self.assertEqual(result.message, "Internal server error")

        asyncio.run(async_test())

    @patch('events.request_event.dumps')
    def test_run_method_sends_correct_response_format(self, mock_dumps: Mock) -> None:
        """
        Test that run method sends response in correct format.

        Parameters:
            mock_dumps (Mock): Mock for the dumps function.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            mock_client = Mock()
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()

            # Mock the action in client.actions
            mock_action = Mock()
            mock_action.run = AsyncMock(
                return_value = ActionResponse(
                    status_code = 200,
                    message = "Success"
                )
            )
            mock_client.actions = {"test_action": mock_action}

            # Mock dumps to return a JSON string
            mock_dumps.return_value = '{"response": "data"}'

            await self.request_event.run(mock_client, mock_websocket)

            # Check that dumps was called with correct response format
            call_args = mock_dumps.call_args[0][0]
            self.assertEqual(call_args["topic"], "test_topic")
            self.assertEqual(call_args["event"], "response")
            self.assertIn("payload", call_args)
            self.assertEqual(call_args["ref"], "test_ref")

        asyncio.run(async_test())

    def test_request_event_override_decorator(self) -> None:
        """
        Test that RequestEvent methods use @override decorator correctly.

        Returns:
            None: This test does not return a value.
        """
        # This test ensures the @override decorator is used properly
        # The methods should work without issues
        description = RequestEvent.description()
        self.assertIsInstance(description, str)

        discriminator = RequestEvent.discriminator()
        self.assertIsInstance(discriminator, str)

    def test_request_event_async_run_signature(self) -> None:
        """
        Test that RequestEvent run method has correct async signature.

        Returns:
            None: This test does not return a value.
        """
        import inspect

        run_method = RequestEvent.run
        signature = inspect.signature(run_method)

        # Should have self, client, and websocket parameters
        params = list(signature.parameters.keys())
        self.assertIn("self", params)
        self.assertIn("client", params)
        self.assertIn("websocket", params)

    def test_request_event_run_method_returns_action_response(self) -> None:
        """
        Test that RequestEvent run method returns ActionResponse type.

        Returns:
            None: This test does not return a value.
        """
        import asyncio

        async def test_run() -> ActionResponse:
            mock_client = Mock()
            mock_websocket = AsyncMock()
            mock_client.actions = {}
            result = await self.request_event.run(mock_client, mock_websocket)
            return result

        result = asyncio.run(test_run())
        self.assertIsInstance(result, ActionResponse)


if __name__ == "__main__":
    from unittest import main
    main()
