import unittest
from json import loads
from models import Event

class TestEventModel(unittest.TestCase):
    def setUp(self):
        self.phx_reply_ok = """{"ref":"1","payload":{"status":"ok","response":{"service":{"id":1,"name":"Service 1"}}},"topic":"backend/service/1","event":"phx_reply"}"""
        self.phx_reply_error = """{"ref":"1","payload":{"status":"error","response":{"reason":"Service not found"}},"topic":"backend/service/1","event":"phx_reply"}"""
        self.service_updated = """{"ref":null,"payload":{"service":{"id":1,"name":"Service 1"}},"topic":"backend/service/1","event":"service_updated"}"""
        self.service_deleted = """{"ref":null,"payload":{"service":{"id":1,"name":"Service 1"}},"topic":"backend/service/1","event":"service_deleted"}"""

    def test_phx_reply_ok(self):
        try:
            Event(**loads(self.phx_reply_ok))
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

    def test_phx_reply_error(self):
        try:
            Event(**loads(self.phx_reply_error))
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

    def test_service_updated(self):
        try:
            Event(**loads(self.service_updated))
            self.assertTrue(True)
        except Exception as e:
            raise Exception(e)

    def test_service_deleted(self):
        try:
            Event(**loads(self.service_deleted))
            self.assertTrue(True)
        except Exception as e:
            raise Exception(e)

if __name__ == '__main__':
    unittest.main()