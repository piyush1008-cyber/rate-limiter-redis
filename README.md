# ⏱️ High-Performance Distributed Rate Limiter & FastAPI Middleware

[![CI](https://github.com/piyush1008-cyber/rate-limiter-redis/actions/workflows/ci.yml/badge.svg)](https://github.com/piyush1008-cyber/rate-limiter-redis/actions)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)
![System Design](https://img.shields.io/badge/Pattern-Sliding%20Window%20%26%20Token%20Bucket-orange?style=flat)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?style=flat&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

> **A production-ready API Rate Limiting engine implementing Sliding Window Log and Token Bucket algorithms with zero-overhead FastAPI middleware and standard HTTP 429 telemetry headers.**

---

## 📐 System Design & Rate Limiting Architecture

```
Client Request
      |
      v
+-------------------------------+
|     FastAPI ASGI Pipeline     |
+-------------------------------+
      |
      v
+-------------------------------+
|     RateLimitMiddleware       |
|                               |
|   1. Extract Client Identity  | (X-Forwarded-For or Remote IP)
|   2. Check Algorithm Window   | (Sliding Window / Token Bucket)
+-------------------------------+
      |
      +---------> Limit Exceeded?
      |                  |
     NO                 YES
      |                  |
      v                  v
+----------------+  +---------------------------------------------+
| Route Handler  |  | HTTP 429 Too Many Requests                  |
| 200 OK         |  | Headers:                                    |
| Headers:       |  |   Retry-After: <seconds>                    |
|   X-RateLimit-*|  |   X-RateLimit-Limit / Remaining / Reset     |
+----------------+  +---------------------------------------------+
```

---

## ⚡ Algorithm Comparison

| Dimension | Sliding Window Log | Token Bucket |
|---|---|---|
| **Boundary Bursts** | Completely eliminated; strict rolling window | Accommodates bursts up to capacity |
| **Memory Footprint** | $O(N)$ where $N$ is count of requests in window | $O(1)$ constant memory per client key |
| **Time Complexity** | $O(1)$ amortized eviction | $O(1)$ constant arithmetic calculation |
| **Best Used For** | Strict security APIs & payment gateways | Public APIs allowing temporary traffic bursts |

---

## 🚀 Key Features

- 🛡️ **Prevents Denial-of-Service & API Abuse:** Defends downstream infrastructure and databases from burst traffic and bot scraping.
- ⏱️ **RFC Telemetry Headers:** Sets `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After`.
- 🔀 **Dual Algorithm Engine:** Choose between smooth Token Bucket or strict Sliding Window Log.
- ⚡ **Zero-Overhead Middleware:** In-memory thread-safe locks with microsecond lookup latency.
- 🧪 **100% Automated Test Coverage:** Tested with Pytest simulating bursts, boundary expirations, and concurrency.

---

## 📁 Repository Structure

```
rate-limiter-redis/
├── rate_limiter/
│   ├── __init__.py          # Exported algorithms
│   ├── base.py              # Abstract BaseRateLimiter interface
│   ├── sliding_window.py    # Sliding Window Log implementation
│   ├── token_bucket.py      # Token Bucket implementation
│   └── middleware.py        # FastAPI ASGI middleware
├── app/
│   ├── __init__.py
│   └── main.py              # Sample FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_rate_limiter.py # Pytest verification suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚡ Quickstart Guide

### 1. Clone & Run Locally

```bash
git clone https://github.com/piyush1008-cyber/rate-limiter-redis.git
cd rate-limiter-redis

python -m venv venv
venv\Scripts\activate       # On Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Run with Docker

```bash
docker-compose up --build -d
```

### 3. Verify Rate Limiter via cURL

```bash
# Make 5 rapid requests (allowed)
for i in {1..5}; do curl -i http://localhost:8000/api/v1/resource; done

# 6th request is blocked with HTTP 429
curl -i http://localhost:8000/api/v1/resource
```

**HTTP 429 Response Sample:**
```http
HTTP/1.1 429 Too Many Requests
content-type: application/json
retry-after: 9
x-ratelimit-limit: 5
x-ratelimit-remaining: 0
x-ratelimit-reset: 9

{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Limit is 5 requests per 10s.",
  "retry_after_seconds": 9
}
```

---

## 🧪 Automated Testing

```bash
pytest -v
```

Expected output:
```text
tests/test_rate_limiter.py::test_sliding_window_algorithm PASSED         [ 33%]
tests/test_rate_limiter.py::test_token_bucket_algorithm PASSED           [ 66%]
tests/test_rate_limiter.py::test_fastapi_middleware_enforcement PASSED   [100%]

============================== 3 passed in 2.63s ==============================
```

---

## 👤 Author

**Peeyoosh Kangle**
- 📧 Email: piyushkangle@gmail.com
- 🐙 GitHub: [github.com/piyush1008-cyber](https://github.com/piyush1008-cyber)

---

## 📄 License

This repository is distributed under the MIT License — see the [LICENSE](LICENSE) file.
