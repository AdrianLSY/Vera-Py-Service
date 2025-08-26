import unittest
from core.plugboard_client import PlugboardClient

class PlugboardClientTest(unittest.TestCase):
    def setUp(self):
        self.client = PlugboardClient()

    def test_client_initialization(self):
        self.assertIsNotNone(self.client)
        self.assertIsInstance(self.client, PlugboardClient)

if __name__ == "__main__":
    unittest.main()
