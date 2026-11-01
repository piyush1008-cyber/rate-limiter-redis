import time
from threading import Lock
from typing import Dict, Tuple
from rate_limiter.base import BaseRateLimiter


class TokenBucketLimiter(BaseRateLimiter):
    """
    Token Bucket Rate Limiter.
    Allows bursts of traffic up to bucket capacity while enforcing a constant average rate.
    Tokens are refilled continuously over time.
    """

    def __init__(self):
        # key -> (current_tokens, last_refill_time)
        self._buckets: Dict[str, Tuple[float, float]] = {}
        self._lock = Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        now = time.time()
        refill_rate = max_requests / window_seconds  # tokens per second

        with self._lock:
            if key not in self._buckets:
                tokens = float(max_requests)
                last_time = now
            else:
                tokens, last_time = self._buckets[key]
                elapsed = now - last_time
                tokens = min(float(max_requests), tokens + elapsed * refill_rate)
                last_time = now

            if tokens >= 1.0:
                tokens -= 1.0
                self._buckets[key] = (tokens, last_time)
                remaining = int(tokens)
                time_to_full = int((max_requests - tokens) / refill_rate)
                return True, remaining, max(time_to_full, 1)
            else:
                self._buckets[key] = (tokens, last_time)
                needed = 1.0 - tokens
                retry_after = int(needed / refill_rate) + 1
                return False, 0, max(retry_after, 1)

    def reset(self, key: str = None):
        with self._lock:
            if key:
                self._buckets.pop(key, None)
            else:
                self._buckets.clear()
