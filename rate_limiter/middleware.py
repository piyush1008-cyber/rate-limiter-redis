from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from rate_limiter.sliding_window import SlidingWindowLimiter
from rate_limiter.token_bucket import TokenBucketLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI HTTP Middleware intercepting inbound requests and enforcing rate limits.
    Injects RFC compliant rate limit headers on all responses.
    """

    def __init__(
        self,
        app,
        max_requests: int = 60,
        window_seconds: int = 60,
        algorithm: str = "sliding_window",
        key_func: Optional[Callable[[Request], str]] = None
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_func = key_func or self._default_client_key

        if algorithm == "token_bucket":
            self.limiter = TokenBucketLimiter()
        else:
            self.limiter = SlidingWindowLimiter()

    @staticmethod
    def _default_client_key(request: Request) -> str:
        """Resolve client IP from headers or direct connection."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "127.0.0.1"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Exclude documentation and health check endpoints
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)

        client_key = f"{self.key_func(request)}:{request.url.path}"
        allowed, remaining, reset_in = self.limiter.is_allowed(
            client_key, self.max_requests, self.window_seconds
        )

        headers = {
            "X-RateLimit-Limit": str(self.max_requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_in),
        }

        if not allowed:
            headers["Retry-After"] = str(reset_in)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit is {self.max_requests} requests per {self.window_seconds}s.",
                    "retry_after_seconds": reset_in
                },
                headers=headers
            )

        response = await call_next(request)
        for k, v in headers.items():
            response.headers[k] = v
        return response
