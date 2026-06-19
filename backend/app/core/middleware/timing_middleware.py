import time
from typing import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.logger import get_logger

logger = get_logger("app.middleware.timing")
SLOW_REQUEST_THRESHOLD_MS = 500.0

class TimingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        response.headers["Server-Timing"] = f'total;dur={duration_ms:.2f};desc="Total request time"'
        response.headers["X-Response-Time-ms"] = f"{duration_ms:.2f}"
        if duration_ms > SLOW_REQUEST_THRESHOLD_MS:
            logger.warning("🐌 SLOW REQUEST: %s %s took %.1fms", request.method, request.url.path, duration_ms)
        return response
