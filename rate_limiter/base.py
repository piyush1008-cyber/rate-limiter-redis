from abc import ABC, abstractmethod
from typing import Tuple


class BaseRateLimiter(ABC):
    """Abstract interface for algorithmic rate limiters."""

    @abstractmethod
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        """
        Evaluate if a request is permissible.
        Returns:
            Tuple[bool, int, int]: (is_allowed, remaining_requests, reset_time_seconds)
        """
        pass
