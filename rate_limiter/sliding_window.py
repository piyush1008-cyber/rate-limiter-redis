import time
from collections import deque
from threading import Lock
from typing import Dict, Tuple
from rate_limiter.base import BaseRateLimiter


class SlidingWindowLimiter(BaseRateLimiter):
    """
    Sliding Window Log Rate Limiter.
    Maintains a millisecond-precision sliding window of past request timestamps per key.
    Eliminates traffic spikes at window boundaries present in fixed-window algorithms.
    """

    def __init__(self):
        self._windows: Dict[str, deque] = {}
        self._lock = Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            if key not in self._windows:
                self._windows[key] = deque()

            q = self._windows[key]

            # Evict timestamps older than the sliding window threshold
            while q and q[0] <= window_start:
                q.popleft()

            if len(q) < max_requests:
                q.append(now)
                remaining = max_requests - len(q)
                reset_in = int(window_seconds - (now - q[0])) if q else window_seconds
                return True, remaining, max(reset_in, 1)
            else:
                remaining = 0
                earliest = q[0]
                retry_after = int(earliest + window_seconds - now)
                return False, remaining, max(retry_after, 1)

    def reset(self, key: str = None):
        """Reset state for a specific key or all keys."""
        with self._lock:
            if key:
                self._windows.pop(key, None)
            else:
                self._windows.clear()
