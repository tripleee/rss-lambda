from __future__ import annotations
from datetime import datetime, timedelta, timezone
import logging

import requests
import feedparser


DEFAULT_AGE = 300  # seconds

logger = logging.getLogger(__name__)


def parse_rss(feedurl: str, age: int = DEFAULT_AGE) -> list[str]:
    """
    Read the RSS feed; return any posts less than five minutes old.
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
        logger.info("Feed is too old: %s", updated)
        return []

    urls: list[str] = []
    delta = timedelta(seconds=age)
    double_delta = timedelta(seconds=age*2)
    within_delta = False
    for entry in rss.entries:
        published = datetime.fromisoformat(entry.published)
        if (now - published) <= delta:
            urls.append(entry.id)
            within_delta = True
        else:
            would_be_within_delta = False
        if (now - published) > double_delta:
            break
        logger.info(
            "URL %s %s", entry.id, "returned" if within_delta else "too old")

    if urls:
        logger.info("Found %d new posts", len(urls))
    else:
        logger.info(
            "No new posts; newest post is %s (published %s), total %i",
            entry.id, published, len(rss.entries))

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
    requests.get(
        "https://hc-ping.com/49036dcb-6946-478f-8570-d79df6eed9d9",
        timeout=10)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(None, None)
