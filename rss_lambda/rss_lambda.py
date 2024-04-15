from __future__ import annotations
from datetime import datetime, timedelta, timezone

import requests
import feedparser


DEFAULT_AGE = 3600  # seconds


def parse_rss(feedurl: str, age: int = DEFAULT_AGE) -> list[str]:
    """
    Read the RSS feed; return any posts less than an hour old.
    """
    rss = feedparser.parse(feedurl)
    try:
        updated_time = rss.feed.updated
    except AttributeError as exc:
        # This can happen when the network goes down (e.g. when your laptop
        # sleeps, or your wifi glitches); the feed dictionary is empty, and
        # the object contains a 'bozo_exception' field with the error
        if hasattr(rss, 'bozo_exception') and rss.bozo_exception:
            print("Bozo exception:", rss.bozo_exception)
        else:
            print("Exception:", type(exc), exc)
        return []
    updated = datetime.fromisoformat(updated_time)
    now = datetime.now(timezone.utc)
    if (now - updated) > timedelta(seconds=age):
        return []

    urls: list[str] = []
    for entry in rss.entries:
        published = datetime.fromisoformat(entry.published)
        if (now - published) > timedelta(seconds=age):
            break
        urls.append(entry.id)
    return urls

def ntfy(url: str) -> None:
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post(
        'http://ntfy.sh/procmail_at_SE', headers=headers, data=url)

def main(event, context) -> None:
    feedurl = 'https://stackexchange.com/feeds/tagsets/158819/procmail' \
        '?sort=newest'
    new = parse_rss(feedurl)
    for url in new:
        ntfy(url)

if __name__ == '__main__':
    main(None, None)
