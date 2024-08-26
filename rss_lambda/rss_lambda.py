from __future__ import annotations
from datetime import datetime, timedelta, timezone
import logging

import requests
import feedparser


DEFAULT_AGE = 300  # seconds

logger = logging.getLogger(__name__)
haz_logging = False


class RSSNotifier:
    def __init__(
            self,
            name: str,
            feedurl: str,
            ntfy_url: str,
            age: int = DEFAULT_AGE
    ) -> None:
        self.name = name
        self.feedurl = feedurl
        self.ntfy_url = ntfy_url
        self.age = age

    def log(self, *args) -> None:
        """
        Wrapper for logging, use print() in AWS
        """
        if haz_logging:
            logger.info(*args)
        else:
            print(args[0] % args[1:])

    def parse_rss(self) -> list[str]:
        """
        Read the RSS feed; return any posts less than five minutes old.
        """
        rss = feedparser.parse(self.feedurl)
        delta = timedelta(seconds=self.age)
        try:
            updated_time = rss.feed.updated
        except AttributeError as exc:
            # This can happen when the network goes down (e.g. when
            # your laptop sleeps, or your wifi glitches); the feed
            # dictionary is empty, and the object contains a
            # 'bozo_exception' field with the error
            if hasattr(rss, 'bozo_exception') and rss.bozo_exception:
                self.log("Bozo exception: %s", rss.bozo_exception)
            else:
                self.log("Exception: (%s) %s", type(exc), exc)
            return []
        updated = datetime.fromisoformat(updated_time)
        now = datetime.now(timezone.utc)
        if (now - updated) > delta:
            self.log("Feed is too old: %s", updated)
            return []

        urls: list[str] = []
        double_delta = timedelta(seconds=self.age*2)
        within_delta = False
        for entry in rss.entries:
            published = datetime.fromisoformat(entry.published)
            if (now - published) <= delta:
                urls.append(entry.id)
                within_delta = True
            else:
                within_delta = False
            if (now - published) > double_delta:
                break
            self.log(
                "URL %s %s", entry.id,
                "returned" if within_delta else "too old")

        if urls:
            self.log("Found %d new posts", len(urls))
        else:
            self.log(
                "No new posts; newest post is %s (published %s), total %i",
                entry.id, published, len(rss.entries))

        return urls

    def ntfy(self, url: str) -> None:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(self.ntfy_url, headers=headers, data=url)

    def ntfy_new(self) -> None:
        urls = self.parse_rss()
        for url in urls:
            self.ntfy(url)


def main(event, context) -> None:
    for feed in (RSSNotifier(
            name='procmail',
            feedurl='https://stackexchange.com/feeds/tagsets/158819/procmail' \
                '?sort=newest',
            ntfy_url='http://ntfy.sh/procmail_at_SE'),
        RSSNotifier(
            name='Awk',
            feedurl='https://stackoverflow.com/feeds/tag?' \
                'tagnames=awk&sort=newest',
            ntfy_url='http://ntfy.sh/SO_Awk')
    ):
        feed.ntfy_new()
    requests.get(
        "https://hc-ping.com/49036dcb-6946-478f-8570-d79df6eed9d9",
        timeout=10)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    haz_logging = True
    main(None, None)
