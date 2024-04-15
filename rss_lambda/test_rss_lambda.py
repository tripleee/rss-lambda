import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

from rss_lambda import parse_rss, main as parse_rss_main


EXPECTED_URLS = ['http://example.com/1', 'http://example.com/2']


class TestParseRss(unittest.TestCase):
    @patch('rss_lambda.requests')
    @patch('rss_lambda.feedparser')
    def test_parse_rss(self, mock_feedparser, mock_requests):
        now = datetime.now(timezone.utc)

        def _minutes_ago(minutes: int) -> str:
            f"""
            Return a time the requested number of minutes ago, relative
            to now ({now}), as an ISO date format string.
            """
            return (now - timedelta(minutes=minutes)).isoformat()
        
        # Set up the mock objects
        mock_feedparser.parse.return_value = MagicMock(
            feed=MagicMock(updated=now.isoformat()),
            entries=[
                MagicMock(
                    published=_minutes_ago(1), id='http://example.com/1'),
                MagicMock(
                    published=_minutes_ago(59), id='http://example.com/2'),
                MagicMock(
                    published=_minutes_ago(61), id='http://example.com/3'),
            ]
        )

        # Call the function
        result = parse_rss('http://example.com/rss')

        # Check the result
        self.assertEqual(result, EXPECTED_URLS)

        # Check that the mock objects were called correctly
        mock_feedparser.parse.assert_called_once_with('http://example.com/rss')

    @patch('rss_lambda.requests.post')
    @patch('rss_lambda.parse_rss')
    def test_main(self, mock_parse_rss, mock_requests_post):
        # Set up the mock objects
        mock_parse_rss.return_value = EXPECTED_URLS
        mock_requests_post.return_value = MagicMock(status_code=200)

        # Call the function
        result = parse_rss_main(None, 'flabbergasted')
        self.assertIsNone(result)

        # Check that the mock objects were called correctly
        mock_parse_rss.assert_called_once()
        calls = mock_requests_post.mock_calls
        self.assertEqual(len(calls), 2)
        for call, expected in zip(calls, EXPECTED_URLS):
            self.assertEqual(call[2]["data"], expected)


if __name__ == '__main__':
    unittest.main()
