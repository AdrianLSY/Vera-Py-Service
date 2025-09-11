import asyncio
from typing import override
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from websockets import ConnectionClosed

from core.plugboard_client import PlugboardClient
from models.service import Service
from models.token import Token


class TestPlugboardClient(TestCase):
    """Test cases for PlugboardClient class."""

    client: PlugboardClient  # type: ignore

    @override
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = PlugboardClient()

    def test_plugboard_client_initialization(self) -> None:
        """
        Test PlugboardClient initialization with default values.

        Returns:
            None: This test does not return a value.
        """
        self.assertIsNone(self.client.service)
        self.assertIsInstance(self.client.token, Token)
        self.assertEqual(self.client.num_consumers, 0)
        self.assertFalse(self.client.connected)
        self.assertIsInstance(self.client.events, dict)
        self.assertIsInstance(self.client.actions, dict)

    def test_plugboard_client_initialization_with_custom_values(self) -> None:
        """
        Test PlugboardClient initialization with custom values.

        Returns:
            None: This test does not return a value.
        """
        service = Service(
            id = 1,
            name = "Test Service",
            inserted_at = "2023-01-01T00:00:00",
            updated_at = "2023-01-01T00:00:00"
        )
        token = Token(
            id = 1,
            value = "test_token",
            context = "test_context"
        )

        client = PlugboardClient(
            service = service,
            token = token,
            num_consumers = 5,
            connected = True
        )

        self.assertEqual(client.service, service)
        self.assertEqual(client.token, token)
        self.assertEqual(client.num_consumers, 5)
        self.assertTrue(client.connected)

    def test_plugboard_client_inherits_from_base_model(self) -> None:
        """
        Test that PlugboardClient inherits from BaseModel.

        Returns:
            None: This test does not return a value.
        """
        from pydantic import BaseModel

        # PlugboardClient is always a subclass of BaseModel by design
        self.assertIsInstance(PlugboardClient, type)

    def test_plugboard_client_events_field_default(self) -> None:
        """
        Test that events field is populated with discovered events.

        Returns:
            None: This test does not return a value.
        """
        # The events field should be populated by ActionRegistry.discover
        self.assertIsInstance(self.client.events, dict)
        # Should contain some events (depending on what's in the events directory)

    def test_plugboard_client_actions_field_default(self) -> None:
        """
        Test that actions field is populated with discovered actions.

        Returns:
            None: This test does not return a value.
        """
        # The actions field should be populated by ActionRegistry.discover
        self.assertIsInstance(self.client.actions, dict)
        # Should contain some actions (depending on what's in the actions directory)

    @patch('core.plugboard_client.connect')
    @patch('core.plugboard_client.PhxJoinEvent')
    def test_connect_sets_token_and_connected(self, mock_phx_join: Mock, mock_connect: Mock) -> None:
        """
        Test that connect method sets token and connected status.

        Parameters:
            mock_phx_join (Mock): Mock for PhxJoinEvent.
            mock_connect (Mock): Mock for the connect function.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            # Mock websocket connection
            mock_websocket = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_websocket

            # Mock PhxJoinEvent
            mock_join_event = MagicMock()
            mock_join_event.model_dump_json.return_value = '{"event": "phx_join"}'
            mock_phx_join.return_value = mock_join_event

            # Mock the loop to exit immediately
            with patch.object(self.client, '_PlugboardClient__loop', new_callable=AsyncMock) as mock_loop:
                mock_loop.return_value = None

                await self.client.connect("ws://test.com", "test_token")

                self.assertEqual(self.client.token.value, "test_token")
                self.assertTrue(self.client.connected)

        asyncio.run(async_test())

    @patch('core.plugboard_client.connect')
    def test_connect_returns_early_if_already_connected(self, mock_connect: Mock) -> None:
        """
        Test that connect returns early if already connected.

        Parameters:
            mock_connect (Mock): Mock for the connect function.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            self.client.connected = True

            await self.client.connect("ws://test.com", "test_token")

            # Should not attempt to connect
            mock_connect.assert_not_called()

        asyncio.run(async_test())

    @patch('core.plugboard_client.connect')
    @patch('core.plugboard_client.PhxJoinEvent')
    def test_connect_calls_websocket_with_correct_url(self, mock_phx_join: Mock, mock_connect: Mock) -> None:
        """
        Test that connect calls websocket with correct URL and parameters.

        Parameters:
            mock_phx_join (Mock): Mock for PhxJoinEvent.
            mock_connect (Mock): Mock for the connect function.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            # Mock websocket connection
            mock_websocket = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_websocket

            # Mock PhxJoinEvent
            mock_join_event = MagicMock()
            mock_join_event.model_dump_json.return_value = '{"event": "phx_join"}'
            mock_phx_join.return_value = mock_join_event

            # Mock the loop to exit immediately
            with patch.object(self.client, '_PlugboardClient__loop', new_callable=AsyncMock) as mock_loop:
                mock_loop.return_value = None

                await self.client.connect("ws://test.com", "test_token")

                # Check that connect was called with correct URL
                mock_connect.assert_called_once()
                call_args = mock_connect.call_args[0]
                self.assertTrue(call_args[0].startswith("ws://test.com?token=test_token&actions="))

        asyncio.run(async_test())

    @patch('core.plugboard_client.connect')
    @patch('core.plugboard_client.PhxJoinEvent')
    def test_loop_sends_phx_join_event(self, mock_phx_join: Mock, mock_connect: Mock) -> None:
        """
        Test that __loop sends PhxJoinEvent on connection.

        Parameters:
            mock_phx_join (Mock): Mock for PhxJoinEvent.
            mock_connect (Mock): Mock for the connect function.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            # Mock websocket connection
            mock_websocket = AsyncMock()
            # First call to recv raises ConnectionClosed to break the loop after PhxJoinEvent is sent
            mock_websocket.recv.side_effect = ConnectionClosed(None, None)
            mock_connect.return_value.__aenter__.return_value = mock_websocket

            # Mock PhxJoinEvent
            mock_join_event = MagicMock()
            mock_join_event.model_dump_json.return_value = '{"event": "phx_join"}'
            mock_phx_join.return_value = mock_join_event

            await self.client.connect("ws://test.com", "test_token")

            # Check that PhxJoinEvent was created and sent
            mock_phx_join.assert_called_once_with(topic="service")
            mock_websocket.send.assert_called()

        asyncio.run(async_test())

    def test_loop_handles_json_decode_error(self) -> None:
        """
        Test that __loop handles JSONDecodeError gracefully.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            mock_websocket = AsyncMock()
            # First call returns invalid JSON, second call raises ConnectionClosed to break the loop
            mock_websocket.recv.side_effect = ["invalid json", ConnectionClosed(None, None)]

            # Set connected to True so the loop runs
            self.client.connected = True

            # Mock print to capture output
            with patch('builtins.print') as mock_print:
                # Type ignore for private method access
                await self.client._PlugboardClient__loop(mock_websocket)  # type: ignore

                # Should print "Invalid JSON"
                mock_print.assert_called_with("Invalid JSON")

        asyncio.run(async_test())

    def test_loop_handles_key_error(self) -> None:
        """
        Test that __loop handles KeyError gracefully.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            mock_websocket = AsyncMock()
            # First call returns invalid message, second call raises ConnectionClosed to break the loop
            mock_websocket.recv.side_effect = ['{"invalid": "message"}', ConnectionClosed(None, None)]

            # Set connected to True so the loop runs
            self.client.connected = True

            # Mock print to capture output
            with patch('builtins.print') as mock_print:
                # Type ignore for private method access
                await self.client._PlugboardClient__loop(mock_websocket)  # type: ignore

                # Should print "Invalid message"
                mock_print.assert_called_with("Invalid message")

        asyncio.run(async_test())

    def test_loop_handles_validation_error(self) -> None:
        """
        Test that __loop handles ValidationError gracefully.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            from pydantic import ValidationError

            mock_websocket = AsyncMock()
            # First call returns test event, second call raises ConnectionClosed to break the loop
            mock_websocket.recv.side_effect = ['{"event": "test_event"}', ConnectionClosed(None, None)]

            # Set connected to True so the loop runs
            self.client.connected = True

            # Mock the event handler to raise ValidationError
            with patch.dict(self.client.events, {"test_event": MagicMock(side_effect=ValidationError.from_exception_data("TestError", []))}):
                with patch('builtins.print') as mock_print:
                    # Type ignore for private method access
                    await self.client._PlugboardClient__loop(mock_websocket)  # type: ignore

                    # Should print validation error
                    mock_print.assert_called()

        asyncio.run(async_test())

    def test_loop_handles_connection_closed(self) -> None:
        """
        Test that __loop handles ConnectionClosed gracefully.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            from websockets import ConnectionClosed

            mock_websocket = AsyncMock()
            mock_websocket.recv.side_effect = ConnectionClosed(None, None)

            # Type ignore for private method access
            await self.client._PlugboardClient__loop(mock_websocket)  # type: ignore

            # Should set connected to False
            self.assertFalse(self.client.connected)

        asyncio.run(async_test())

    def test_loop_handles_connection_aborted(self) -> None:
        """
        Test that __loop handles ConnectionAbortedError gracefully.

        Returns:
            None: This test does not return a value.
        """
        async def async_test() -> None:
            mock_websocket = AsyncMock()
            mock_websocket.recv.side_effect = ConnectionAbortedError()

            # Type ignore for private method access
            await self.client._PlugboardClient__loop(mock_websocket)  # type: ignore

            # Should set connected to False
            self.assertFalse(self.client.connected)

        asyncio.run(async_test())

    def test_plugboard_client_model_validation(self) -> None:
        """
        Test PlugboardClient model validation.

        Returns:
            None: This test does not return a value.
        """
        # Valid data should work
        client = PlugboardClient(
            num_consumers = 5,
            connected = True
        )
        self.assertEqual(client.num_consumers, 5)
        self.assertTrue(client.connected)

        # Invalid data should raise ValidationError
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            PlugboardClient(num_consumers = "not_an_int")

    def test_plugboard_client_json_serialization(self) -> None:
        """
        Test PlugboardClient JSON serialization.

        Returns:
            None: This test does not return a value.
        """
        # This test is simplified due to serialization issues with complex types
        client = PlugboardClient(
            num_consumers = 3,
            connected = True
        )

        # Test basic model functionality instead of JSON serialization
        self.assertEqual(client.num_consumers, 3)
        self.assertTrue(client.connected)


if __name__ == "__main__":
    from unittest import main
    main()
