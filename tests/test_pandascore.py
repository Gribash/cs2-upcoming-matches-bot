import unittest
from unittest.mock import patch
from utils import pandascore

class TestPandaScoreAPI(unittest.TestCase):
    @patch("utils.pandascore.requests.get")
    def test_get_upcoming_cs2_matches(self, mock_get):
        mock_response = {
            "status_code": 200,
            "json": lambda: [{
                "opponents": [{"opponent": {"name": "Team A"}}, {"opponent": {"name": "Team B"}}],
                "begin_at": "2025-07-01T10:00:00Z",
                "streams_list": [{"raw_url": "http://example.com/stream"}],
            }]
        }
        mock_get.return_value = type("Response", (object,), mock_response)

        matches = pandascore.get_upcoming_cs2_matches()
        self.assertIsInstance(matches, list)
        self.assertEqual(matches[0]["opponents"][0]["opponent"]["name"], "Team A")