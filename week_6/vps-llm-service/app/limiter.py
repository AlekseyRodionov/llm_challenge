import time
from typing import Optional

from app.config import RATE_LIMIT_SECONDS


class RateLimiter:
    def __init__(self):
        self._requests: dict[str, float] = {}

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        last_request = self._requests.get(ip)

        if last_request is None:
            self._requests[ip] = now
            return True

        if now - last_request >= RATE_LIMIT_SECONDS:
            self._requests[ip] = now
            return True

        return False

    def time_until_allowed(self, ip: str) -> Optional[float]:
        last_request = self._requests.get(ip)
        if last_request is None:
            return None
        elapsed = time.time() - last_request
        remaining = RATE_LIMIT_SECONDS - elapsed
        return max(0, remaining)


limiter = RateLimiter()
