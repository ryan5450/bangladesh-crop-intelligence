"""Per-domain rate limiter to maintain respectful politeness with government portals."""

import asyncio
import time
from typing import Dict
from urllib.parse import urlparse

from config import DEFAULT_RATE_LIMIT_DELAY


class DomainRateLimiter:
    """Thread-safe and async-safe domain rate limiter."""

    def __init__(self, delay_seconds: float = DEFAULT_RATE_LIMIT_DELAY):
        self.delay = delay_seconds
        self._last_request_times: Dict[str, float] = {}

    def _get_domain(self, url: str) -> str:
        return urlparse(url).netloc.lower()

    async def wait_for_domain(self, url: str) -> None:
        """Asynchronously wait until the required delay has elapsed for this domain."""
        domain = self._get_domain(url)
        last_time = self._last_request_times.get(domain, 0.0)
        now = time.time()
        elapsed = now - last_time

        if elapsed < self.delay:
            wait_time = self.delay - elapsed
            await asyncio.sleep(wait_time)

        self._last_request_times[domain] = time.time()

    def wait_sync(self, url: str) -> None:
        """Synchronously wait until the required delay has elapsed for this domain."""
        domain = self._get_domain(url)
        last_time = self._last_request_times.get(domain, 0.0)
        now = time.time()
        elapsed = now - last_time

        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        self._last_request_times[domain] = time.time()

