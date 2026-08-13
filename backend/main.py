import logging
from collections import defaultdict, deque
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import app_tokens
from app.api.routes.market import app_prices
from app.api.routes.products import task
from app.api.routes.users import app_users
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)


class LoginRateLimitMiddleware:
    """Small per-process guard for credential stuffing; use a shared limiter when scaled."""

    def __init__(self, app, attempts: int = 10, window_seconds: int = 60):
        self.app = app
        self.attempts = attempts
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

    async def __call__(self, scope, receive, send):
        protected_paths = {
            "/token",
            "/api/users/create",
            "/auth/oauth/exchange",
            "/auth/password/forgot",
            "/auth/password/verify-otp",
            "/auth/password/reset",
        }
        if (
            scope["type"] == "http"
            and scope["path"] in protected_paths
            and scope["method"] == "POST"
        ):
            now = monotonic()
            client = scope.get("client")
            key = client[0] if client else "unknown"
            history = self.requests[key]
            while history and history[0] <= now - self.window_seconds:
                history.popleft()
            if len(history) >= self.attempts:
                response = JSONResponse(
                    {"detail": "Demasiados intentos. Inténtalo de nuevo más tarde."},
                    status_code=429,
                    headers={"Retry-After": str(self.window_seconds)},
                )
                await response(scope, receive, send)
                return
            history.append(now)
        await self.app(scope, receive, send)


def create_app() -> FastAPI:
    settings.validate_security()
    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        docs_url=None if settings.environment == "production" else "/docs",
        redoc_url=None if settings.environment == "production" else "/redoc",
        openapi_url=None if settings.environment == "production" else "/openapi.json",
    )
    application.add_middleware(LoginRateLimitMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    for router in (app_users, app_tokens, task, app_prices):
        application.include_router(router)

    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @application.get("/", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return application


app = create_app()
