import unittest
from models.token import Token
from models.service import Service
from core.action_model import ActionModel
from core.action_runner import ActionRunner
from events.request_event import RequestEvent
from events.phx_join_event import PhxJoinEvent
from core.action_registry import ActionRegistry
from events.phx_reply_event import PhxReplyEvent
from events.token_created_event import TokenCreatedEvent
from events.token_deleted_event import TokenDeletedEvent
from events.service_updated_event import ServiceUpdatedEvent
from events.service_deleted_event import ServiceDeletedEvent
from events.consumers_connected_event import ConsumerConnectedEvent

class ActionRegistryTest(unittest.TestCase):
    def test_get_events(self):
        expected = {
            "phx_reply": PhxReplyEvent,
            "phx_join": PhxJoinEvent,
            "num_consumers": ConsumerConnectedEvent,
            "service_updated": ServiceUpdatedEvent,
            "service_deleted": ServiceDeletedEvent,
            "token_created": TokenCreatedEvent,
            "token_deleted": TokenDeletedEvent,
            "request": RequestEvent
        }
        actions = ActionRegistry.discover("events", ActionRunner)
        self.assertEqual(expected, actions)

    def test_get_models(self):
        expected = {
            "Token": Token,
            "Service": Service
        }
        actions = ActionRegistry.discover("models", ActionModel)
        self.assertEqual(expected, actions)


if __name__ == "__main__":
    unittest.main()
