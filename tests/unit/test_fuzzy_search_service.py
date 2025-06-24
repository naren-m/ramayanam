import unittest
from unittest.mock import MagicMock, patch
from api.services.fuzzy_search_service import FuzzySearchService

class TestFuzzySearchService(unittest.TestCase):

    def setUp(self):
        # Mocking the ramayanam_data structure
        self.mock_ramayanam_data = MagicMock()
        self.mock_ramayanam_data.kandas = {
            1: MagicMock(),
            2: MagicMock()
        }
        self.service = FuzzySearchService(self.mock_ramayanam_data)

    @patch('api.services.fuzzy_search_service.FuzzySearchService.search_translation_in_kanda_fuzzy')
    def test_search_translation_fuzzy(self, mock_search_translation_in_kanda_fuzzy):
        """
        Test the fuzzy search translation functionality.

        This test verifies that the `search_translation_fuzzy` method correctly retrieves
        translations based on a given query. It mocks the `search_translation_in_kanda_fuzzy`
        function to return predefined results, allowing for controlled testing of the service's
        behavior.

        Assertions:
        - The number of results returned matches the expected count.
        - Each result contains the correct `sloka_id`, `translation`, and `ratio`.
        - The mocked function is called with the expected parameters.

        Parameters:
        - mock_search_translation_in_kanda_fuzzy: Mock object for the fuzzy search function.
        """
        # Mocking the return value of search_translation_in_kanda_fuzzy
        mock_search_translation_in_kanda_fuzzy.side_effect = [
            [{'sloka_id': 1, 'translation': 'translation1', 'ratio': 80}],
            [{'sloka_id': 2, 'translation': 'translation2', 'ratio': 75}]
        ]

        query = "test query"
        results = self.service.search_translation_fuzzy(query)

        # Assertions
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['sloka_id'], 1)
        self.assertEqual(results[0]['translation'], 'translation1')
        self.assertEqual(results[0]['ratio'], 80)
        self.assertEqual(results[1]['sloka_id'], 2)
        self.assertEqual(results[1]['translation'], 'translation2')
        self.assertEqual(results[1]['ratio'], 75)

        # Verify that search_translation_in_kanda_fuzzy was called with correct parameters
        mock_search_translation_in_kanda_fuzzy.assert_any_call(1, query.lower(), 70)
        mock_search_translation_in_kanda_fuzzy.assert_any_call(2, query.lower(), 70)



if __name__ == '__main__':
    unittest.main()