"""In-memory sliding-window rate limiting per client IP.

Counts are kept per process, so on serverless hosting they are approximate.
"""

import math
import time
from bisect import bisect_right
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, Request

from app.config import settings


class RateLimiter:
    def __init__(
        self,
        limits: list[tuple[int, float]],
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """limits: (max requests, window in seconds) pairs."""
        self.limits = limits
        self.clock = clock
        self.hits: dict[str, deque[float]] = {}

    def hit(self, key: str) -> float | None:
        """Records a request. Returns seconds to wait if the key is over a limit."""
        now = self.clock()
        hits = self.hits.setdefault(key, deque())
        longest = max(window for _, window in self.limits)
        while hits and hits[0] <= now - longest:
            hits.popleft()

        retry_after = 0.0
        for maximum, window in self.limits:
            start = bisect_right(hits, now - window)
            if len(hits) - start >= maximum:
                oldest = hits[len(hits) - maximum]
                retry_after = max(retry_after, oldest + window - now)
        if retry_after:
            return retry_after
        hits.append(now)
        return None


limiter = RateLimiter(
    [(settings.rate_limit_per_minute, 60), (settings.rate_limit_per_day, 86400)]
)


def rate_limit(request: Request) -> None:
    """FastAPI dependency: rejects requests over the per-IP limits with 429."""
    key = request.client.host if request.client else "unknown"
    retry_after = limiter.hit(key)
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a moment and try again.",
            headers={"Retry-After": str(math.ceil(retry_after))},
        )
