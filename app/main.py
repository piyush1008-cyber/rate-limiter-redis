from fastapi import FastAPI
from rate_limiter.middleware import RateLimitMiddleware

app = FastAPI(
    title="Distributed API Rate Limiter Service",
    version="1.0.0",
    description="⚡ Production API rate limiter implementing Token Bucket and Sliding Window Log algorithms with custom HTTP headers."
)

# Attach rate limiting middleware: 5 requests per 10 seconds for demo
app.add_middleware(
    RateLimitMiddleware,
    max_requests=5,
    window_seconds=10,
    algorithm="sliding_window"
)


@app.get("/")
def read_root():
    return {
        "service": "Rate Limiter API",
        "status": "online",
        "rate_limit_policy": "5 requests per 10 seconds per IP"
    }


@app.get("/health")
def health():
    # Excluded from rate limits
    return {"status": "healthy"}


@app.get("/api/v1/resource")
def get_protected_resource():
    return {
        "message": "Resource accessed successfully",
        "data": [1, 2, 3, 4, 5]
    }
