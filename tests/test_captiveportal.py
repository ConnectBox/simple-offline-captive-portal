import unittest

import captiveportal


class CaptiveportalTestCase(unittest.TestCase):

    def setUp(self):
        self.app = captiveportal.app.test_client()

    def test_index(self):
        rv = self.app.get('/')
        self.assertIn('Welcome to Simple Offline Captive Portal', rv.data.decode())


if __name__ == '__main__':
    unittest.main()
