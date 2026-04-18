import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

from rss_lambda import RSSNotifier, main as parse_rss_main


TEST_ENV = {
    'NTFY_PROCMAIL_URL': 'http://ntfy.example.com/procmail',
    'NTFY_AWK_URL': 'http://ntfy.example.com/awk',
    'HC_PING_URL': 'https://hc-ping.example.com/test-uuid',
}


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

        # Call the method
        notifier = RSSNotifier('test', 'http://example.com/rss', '', 3600)
        result = notifier.parse_rss()
        self.assertEqual(result, EXPECTED_URLS)

        # Check that the mock objects were called correctly
        mock_feedparser.parse.assert_called_once_with('http://example.com/rss')

    @patch.dict(os.environ, TEST_ENV)
    @patch('rss_lambda.requests.get')
    @patch('rss_lambda.requests.post')
    @patch('rss_lambda.RSSNotifier.parse_rss')
    def test_main(
            self, mock_parse_rss, mock_requests_post, mock_requests_get):
        # Set up the mock objects
        mock_parse_rss.return_value = EXPECTED_URLS
        mock_requests_post.return_value = MagicMock(status_code=200)
        mock_requests_get.return_value = MagicMock(status_code=200)

        # Call the function
        result = parse_rss_main(None, 'flabbergasted')
        self.assertIsNone(result)

        # Check that the mock objects were called correctly
        # parse_rss is called once per feed (2 feeds)
        self.assertEqual(mock_parse_rss.call_count, 2)
        # ntfy is called once per URL per feed (2 URLs × 2 feeds)
        calls = mock_requests_post.mock_calls
        self.assertEqual(len(calls), len(EXPECTED_URLS) * 2)
        posted = [call[2]["data"] for call in calls]
        for url in EXPECTED_URLS:
            self.assertIn(url, posted)
        mock_requests_get.assert_called_once_with(
            TEST_ENV['HC_PING_URL'], timeout=10)


if __name__ == '__main__':
    unittest.main()
