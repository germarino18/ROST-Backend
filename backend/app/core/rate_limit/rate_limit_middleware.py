from typing import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.logger import get_logger
from app.core.rate_limit.rate_limiter import RateLimiter

logger = get_logger("app.middleware.rate_limit")

RATE_LIMIT_DEFAULT_PER_MINUTE = 60
RATE_LIMIT_DEFAULT_BURST = 10
RATE_LIMIT_AUTH_PER_MINUTE = 5
RATE_LIMIT_AUTH_BURST = 3

class RateLimitMiddleware(BaseHTTPMiddleware):
    _instances: list["RateLimitMiddleware"] = []

    AUTH_PATHS: tuple[str, ...] = ("/api/v1/auth/login", "/api/v1/auth/register")
    EXCLUDED_PATHS: set[str] = {"/health", "/", "/favicon.ico", "/openapi.json", "/docs", "/redoc"}

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.default_limiter = RateLimiter(capacity=RATE_LIMIT_DEFAULT_BURST, refill_rate_per_minute=RATE_LIMIT_DEFAULT_PER_MINUTE)
        self.auth_limiter = RateLimiter(capacity=RATE_LIMIT_AUTH_BURST, refill_rate_per_minute=RATE_LIMIT_AUTH_PER_MINUTE)
        RateLimitMiddleware._instances.append(self)

    @classmethod
    def reset_all_limiters(cls) -> None:
        for instance in cls._instances:
            instance.default_limiter.reset_all()
            instance.auth_limiter.reset_all()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        limiter = self.auth_limiter if any(request.url.path.startswith(p) for p in self.AUTH_PATHS) else self.default_limiter
        client_key = self._get_client_key(request)

        if not limiter.is_allowed(client_key):
            logger.warning("Rate limit exceeded: key=%s path=%s", client_key, request.url.path)
            seconds_until_next_token = int(1 / max(limiter.refill_rate, 0.001))
            return Response(
                content=(
                    '{"error":{"code":"rate_limit_exceeded",'
                    '"message":"Demasiadas peticiones. Intenta de nuevo más tarde.",'
                    f'"retry_after_seconds":{seconds_until_next_token}}}}}'
                ),
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(seconds_until_next_token), "X-RateLimit-Limit": str(int(limiter.capacity)), "X-RateLimit-Remaining": "0"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(int(limiter.capacity))
        response.headers["X-RateLimit-Remaining"] = str(max(0, int(limiter.capacity - 1)))
        return response

    @staticmethod
    def _get_client_key(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        if request.client:
            return f"ip:{request.client.host}"
        return "ip:unknown"
