# Spider for finging broken links.
#
#   scrapy crawl spider1 -o ./logs/spider1-log.csv

from datetime import datetime, timezone
import scrapy
from scrapy.http.response.text import TextResponse
from scrapy.exceptions import IgnoreRequest
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


def isodate():
    """Helper to return current date in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


class Spider1(scrapy.Spider):
    name = "spider1"
    start_urls = [
        'http://gw.tnode.com/about',
    ]
    follow_urls = [
        'http://gw.tnode.com/about',
    ]
    skip_urls = [
        'mailto:',
    ]
    old_year = datetime.now().year - 1
    # analytics_ids = []

    def start_requests(self):
        for link in self.start_urls:
            meta = {
                'from_url': 'start_urls',
            }
            yield scrapy.Request(link, callback=self.parse, errback=self.errback, meta=meta)

    def parse(self, response):
        """Parse successful response."""
        if not isinstance(response, TextResponse):  # skip non-text responses
            return

        # by default everything is ok
        status = 'Ok'
        details = ''

        response_body = response.body.decode('utf-8')

        if f" {self.old_year} " in response_body:  # check for old year
            status = 'OldYear'
            details = f"Found year {self.old_year}"

        # elif not any([ (i in response_body) for i in self.analytics_ids ]):  # missing analytics
        #     status = 'MissingAnalytics'
        #     details = f"Missing Analytics ID ({self.analytics_ids})"

        # yield item
        if status != 'Ok':
            self.logger.error(f"{status}: {details}")
            yield {
                'status': status,
                'date': isodate(),
                'url': response.url,
                'from_url': response.meta['from_url'],
                'details': details,
            }

        if self.should_follow(response.url):
            for link in response.css('a::attr(href)'):
                if self.should_skip(link.get()):
                    continue
                meta = {
                    'from_url': response.url,
                }
                yield response.follow(link, callback=self.parse, errback=self.errback, meta=meta)

    def errback(self, failure):
        """Handle spider error."""

        if failure.check(HttpError):  # HTTP error
            response = failure.value.response
            status = 'HttpError'
            details = f"HTTP {response.status} on {response.url}"

        elif failure.check(IgnoreRequest):  # forbidden by robots.txt
            status = 'IgnoreRequest'
            details = f"{failure.getErrorMessage()}"

        elif failure.check(DNSLookupError):  # can not resolve DNS
            status = 'DNSLookupError'
            details = f"{failure.getErrorMessage()}"

        elif failure.check(TimeoutError, TCPTimedOutError):  # connection refused
            status = 'TimeoutError'
            details = f"{failure.getErrorMessage()}"

        else:  # unknown error
            status = 'Unknown'
            details = repr(failure)

        # yield item
        self.logger.error(f"{status}: {details}")
        yield {
            'status': status,
            'date': isodate(),
            'url': failure.request.url,
            'from_url': failure.request.meta['from_url'],
            'details': details,
        }

    def should_skip(self, url):
        for skip_url in self.skip_urls:
            if url.startswith(skip_url):
                return True
        return False

    def should_follow(self, url):
        for follow_url in self.follow_urls:
            if url.startswith(follow_url):
                return True
        return False
