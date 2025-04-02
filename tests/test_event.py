import unittest
from json import loads
from models import Event

class TestEventModel(unittest.TestCase):
    def test_phx_reply_ok(self):
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
        actual = Event(**loads(input)).model_dump()
        self.assertEqual(actual, expected)

    def test_phx_reply_error(self):
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
        actual = Event(**loads(input)).model_dump()
        self.assertEqual(actual, expected)

    def test_service_updated(self):
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
        actual = Event(**loads(input)).model_dump()
        self.assertEqual(actual, expected)

    def test_service_deleted(self):
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
        actual = Event(**loads(input)).model_dump()
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
