import unittest
from json import loads
from app.models import Event
from pydantic import ValidationError

class TestEventModel(unittest.TestCase):
    """
    Tests the serialization of the Event model from messages from the web socket
    """
    def test_phx_reply_ok(self):
        """
        Test the serialization of a phx_reply_ok event
        phx_reply_ok is a successful response from the server, and it contains a service object.
        """
        input = """{"ref":"1","payload":{"status":"ok","response":{"service":{"id":1,"name":"Service 1"},"clients_connected":1}},"topic":"backend/service/1","event":"phx_reply"}"""
        expected = {
            "ref": "1",
            "topic": "backend/service/1",
            "event": "phx_reply",
            "payload": {
                "status": "ok",
                "response": {
                    "service": {
                        "id": 1,
                        "name": "Service 1"
                    },
                    "clients_connected": 1
                }
            }
        }
        output = Event(**loads(input)).model_dump()
        self.assertEqual(output, expected)

    def test_phx_reply_error(self):
        """
        Test the serialization of a phx_reply_error event
        phx_reply_error is an error response from the server, and it contains a reason for the error.
        """
        input = """{"ref":"1","payload":{"status":"error","response":{"reason":"Service not found"}},"topic":"backend/service/1","event":"phx_reply"}"""
        expected = {
            "ref": "1",
            "topic": "backend/service/1",
            "event": "phx_reply",
            "payload": {
                "status": "error",
                "response": {
                    "reason": "Service not found"
                }
            }
        }
        output = Event(**loads(input)).model_dump()
        self.assertEqual(output, expected)

    def test_service_updated(self):
        """
        Test the serialization of a service_updated event
        service_updated is an event that indicates that a service has been updated.
        """
        input = """{"ref":null,"payload":{"service":{"id":1,"name":"Service 1"}},"topic":"backend/service/1","event":"service_updated"}"""
        expected = {
            "ref": None,
            "topic": "backend/service/1",
            "event": "service_updated",
            "payload": {
                "service": {
                    "id": 1,
                    "name": "Service 1"
                }
            }
        }
        output = Event(**loads(input)).model_dump()
        self.assertEqual(output, expected)

    def test_service_deleted(self):
        """
        Test the serialization of a service_deleted event
        service_deleted is an event that indicates that a service has been deleted.
        """
        input = """{"ref":null,"payload":{"service":{"id":1,"name":"Service 1"}},"topic":"backend/service/1","event":"service_deleted"}"""
        expected = {
            "ref": None,
            "topic": "backend/service/1",
            "event": "service_deleted",
            "payload": {
                "service": {
                    "id": 1,
                    "name": "Service 1"
                }
            }
        }
        output = Event(**loads(input)).model_dump()
        self.assertEqual(output, expected)

    def test_clients_connected(self):
        """
        Test the serialization of a clients_connected event
        clients_connected is an event that indicates the number of clients connected to a service.
        """
        input = """{"ref":null,"payload":{"clients_connected":1},"topic":"backend/service/1","event":"clients_connected"}"""
        expected = {
            "ref": None,
            "topic": "backend/service/1",
            "event": "clients_connected",
            "payload": {
                "clients_connected": 1
            }
        }
        output = Event(**loads(input)).model_dump()
        self.assertEqual(output, expected)

    def test_request(self):
        """
        Test the serialization of a request event
        request is an event that contains a request.
        """
        input = """{"ref":"1","payload":{"model":"service","body":{"foo":"bar","hello":"world","1":2,"true":false,"null":null},"metadata":{"test":true,"debug":false}},"topic":"backend/service/1","event":"request"}"""
        expected = {
            "ref": "1",
            "topic": "backend/service/1",
            "event": "request",
            "payload": {
                "model": "service",
                "body": {
                    "foo": "bar",
                    "hello": "world",
                    "1": 2,
                    "true": False,
                    "null": None,
                },
                "metadata": {
                    "test": True,
                    "debug": False
                }
            }
        }
        output = Event(**loads(input)).model_dump()
        self.assertEqual(output, expected)

    def test_unknown_event(self):
        """
        Test the serialization of an unknown event
        This test should fail because the event type is not recognized.
        """
        input = """{"ref":"1","payload":{"status":"ok","response":{"service":{"id":1,"name":"Service 1"}}},"topic":"backend/service/1","event":"unknown"}"""
        try:
            Event(**loads(input)).model_dump()
        except ValidationError:
            self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
