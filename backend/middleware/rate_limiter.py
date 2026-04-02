"""Rate Limiter Middleware — sliding window rate limiting.

Limits API requests per IP address to prevent abuse.
Uses in-memory storage by default, can be upgraded to Redis.
"""

from __future__ import annotations
from typing import Dict, List
from fastapi import Request, HTTPException  # type: ignore
from starlette.middleware.base import BaseHTTPMiddleware  # type: ignore
import time


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter.
    
    Limits each IP to a configurable number of requests per minute.
    Exempt paths (like health checks) are not rate limited.
    """

    def __init__(self, app, requests_per_minute: int = 30):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window = 60  # seconds
        self._requests: Dict[str, List[float]] = {}
        self._exempt_paths = {"/", "/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip rate limiting for exempt paths and OPTIONS
        if path in self._exempt_paths or request.method == "OPTIONS":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window

        # Clean old entries and get current window
        if client_ip not in self._requests:
            self._requests[client_ip] = []

        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > window_start
        ]

        if len(self._requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
            )

        self._requests[client_ip].append(now)

        # Periodic cleanup to prevent memory leak
        if len(self._requests) > 10000:
            cutoff = now - self.window * 2
            self._requests = {
                ip: [t for t in times if t > cutoff]
                for ip, times in self._requests.items()
                if any(t > cutoff for t in times)
            }

        return await call_next(request)
