from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _csv(name: str, default: str) -> tuple[str, ...]:
    return tuple(
        value.strip() for value in os.getenv(name, default).split(",") if value.strip()
    )


def _cors_origins() -> tuple[str, ...]:
    configured = _csv("CORS_ORIGINS", os.getenv("FRONTED_URL", ""))
    if os.getenv("APP_ENV", "development").lower() != "production":
        configured += ("http://localhost:5173", "http://127.0.0.1:5173")
    return tuple(dict.fromkeys(configured))


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "WAC Energy API")
    environment: str = os.getenv("APP_ENV", "development")
    cors_origins: tuple[str, ...] = _cors_origins()
    access_token_secret: str = os.getenv("ACCESS_TOKEN_SECRET", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    max_market_range_days: int = int(os.getenv("MAX_MARKET_RANGE_DAYS", "366"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    otp_expire_minutes: int = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))
    otp_resend_seconds: int = int(os.getenv("OTP_RESEND_SECONDS", "60"))
    otp_max_attempts: int = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_from_number: str = os.getenv("TWILIO_FROM_NUMBER", "")
    backend_url: str = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    facebook_client_id: str = os.getenv("FACEBOOK_CLIENT_ID", "")
    facebook_client_secret: str = os.getenv("FACEBOOK_CLIENT_SECRET", "")
    instagram_client_id: str = os.getenv("INSTAGRAM_CLIENT_ID", "")
    instagram_client_secret: str = os.getenv("INSTAGRAM_CLIENT_SECRET", "")

    def validate_security(self) -> None:
        if not self.access_token_secret:
            raise RuntimeError("ACCESS_TOKEN_SECRET is required")
        if self.algorithm not in {"HS256", "HS384", "HS512"}:
            raise RuntimeError("ALGORITHM must be an allowed HMAC algorithm")
        if self.environment == "production" and len(self.access_token_secret) < 32:
            raise RuntimeError(
                "ACCESS_TOKEN_SECRET must contain at least 32 characters in production"
            )


settings = Settings()
