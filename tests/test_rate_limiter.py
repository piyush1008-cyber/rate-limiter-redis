import time
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from rate_limiter.sliding_window import SlidingWindowLimiter
from rate_limiter.token_bucket import TokenBucketLimiter
from rate_limiter.middleware import RateLimitMiddleware


def test_sliding_window_algorithm():
    limiter = SlidingWindowLimiter()
    key = "test_user_1"
    max_req = 3
    window = 2

    # First 3 allowed
    assert limiter.is_allowed(key, max_req, window)[0] is True
    assert limiter.is_allowed(key, max_req, window)[0] is True
    assert limiter.is_allowed(key, max_req, window)[0] is True

    # 4th blocked
    allowed, remaining, reset_in = limiter.is_allowed(key, max_req, window)
    assert allowed is False
    assert remaining == 0
    assert reset_in >= 1

    # After window elapsed -> allowed again
    time.sleep(2.1)
    assert limiter.is_allowed(key, max_req, window)[0] is True


def test_token_bucket_algorithm():
    limiter = TokenBucketLimiter()
    key = "test_bucket_user"
    capacity = 2
    window = 2  # refill rate = 1 token/sec

    assert limiter.is_allowed(key, capacity, window)[0] is True
    assert limiter.is_allowed(key, capacity, window)[0] is True

    # Empty bucket -> blocked
    allowed, remaining, retry_after = limiter.is_allowed(key, capacity, window)
    assert allowed is False
    assert remaining == 0


def test_fastapi_middleware_enforcement():
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=3,
        window_seconds=5,
        algorithm="sliding_window"
    )

    @app.get("/items")
    def get_items():
        return {"items": []}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    client = TestClient(app)

    # 1. First 3 requests succeed with headers
    for i in range(3):
        res = client.get("/items")
        assert res.status_code == 200
        assert res.headers["X-RateLimit-Limit"] == "3"
        assert int(res.headers["X-RateLimit-Remaining"]) == 2 - i

    # 2. 4th request must trigger HTTP 429
    res_blocked = client.get("/items")
    assert res_blocked.status_code == 429
    assert res_blocked.json()["error"] == "Rate limit exceeded"
    assert "Retry-After" in res_blocked.headers

    # 3. Health endpoint is exempt from rate limits
    for _ in range(5):
        res_health = client.get("/health")
        assert res_health.status_code == 200
