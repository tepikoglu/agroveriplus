"""Middleware: rate limiting + request logging."""

import logging
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("agroveri")

# ─── Rate Limiter ────────────────────────────────────────
# In-memory sliding window. Production: swap to Redis.

_buckets: dict[str, list[float]] = defaultdict(list)

# Limits per path prefix
RATE_LIMITS = {
    "/api/auth/login": (5, 60),       # 5 req / 60s
    "/api/auth/register": (3, 60),    # 3 req / 60s
    "/api/auth/refresh": (10, 60),    # 10 req / 60s
    "/api/certificates/upload": (10, 60),  # 10 req / 60s
    "/api/certificates/verify": (30, 60),  # 30 req / 60s
}
DEFAULT_LIMIT = (60, 60)  # 60 req / 60s for everything else


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting in test environment
        from app.config import settings
        if settings.app_env == "testing":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Find matching limit
        max_requests, window = DEFAULT_LIMIT
        for prefix, limit in RATE_LIMITS.items():
            if path.startswith(prefix):
                max_requests, window = limit
                break

        key = f"{client_ip}:{path}"
        now = time.time()
        _buckets[key] = [t for t in _buckets[key] if now - t < window]

        if len(_buckets[key]) >= max_requests:
            logger.warning(f"Rate limit hit: {client_ip} → {path}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(window)},
            )

        _buckets[key].append(now)
        return await call_next(request)


# ─── Request Logging ─────────────────────────────────────

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000)
        client_ip = request.client.host if request.client else "-"
        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} ({duration}ms) [{client_ip}]"
        )
        return response
