# tests.py

import unittest

from api import app

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_search_sloka_fuzzy(self):
        response = self.app.get('/api/ramayanam/slokas/fuzzy-search?query=hanuman')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

