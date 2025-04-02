import unittest
from json import loads
from models import Event

class TestEventModel(unittest.TestCase):
    """
    Tests the serialization of the Event model from messages from the web socket
    """
    def test_phx_reply_ok(self):
        """
        Test the serialization of a phx_reply_ok event
        phx_reply_ok is a successful response from the server, and it contains a service object.
        """
        input = """{"ref":"1","payload":{"status":"ok","response":{"service":{"id":1,"name":"Service 1"}}},"topic":"backend/service/1","event":"phx_reply"}"""
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
                    }
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

if __name__ == '__main__':
    unittest.main()
