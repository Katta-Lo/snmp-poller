import unittest
from poller import validate_config

#Imports validate_config from poller.py

#Function: ValueError if config misses important information

class TestConfig(unittest.TestCase):
    def test_missing_targets(self):
        with self.assertRaises(ValueError):
            validate_config({})

if __name__ == "__main__":
    unittest.main()
