from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _csv(name: str, default: str) -> tuple[str, ...]:
    return tuple(value.strip() for value in os.getenv(name, default).split(",") if value.strip())


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
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    def validate_security(self) -> None:
        if self.environment == "production" and not self.access_token_secret:
            raise RuntimeError("ACCESS_TOKEN_SECRET es obligatorio en producción")


settings = Settings()
