from datetime import timedelta

import jwt
from types import SimpleNamespace

import app.repositories.tokens as token_service
from app.core.config import settings
from app.repositories.tokens import create_access_token, verify_password
from app.repositories.users import encrypt_password


def test_password_is_hashed_and_verifiable() -> None:
    password = "correct-horse-battery-staple"
    hashed = encrypt_password(password)
    assert hashed != password
    import asyncio
    assert asyncio.run(verify_password(password, hashed)) is True


def test_access_token_contains_subject(monkeypatch) -> None:
    monkeypatch.setattr(token_service, "settings", SimpleNamespace(access_token_secret="unit-test-secret", algorithm="HS256", access_token_expire_minutes=60))
    token = create_access_token({"sub": "user@example.com"}, timedelta(minutes=5))
    payload = jwt.decode(token, "unit-test-secret", algorithms=[settings.algorithm])
    assert payload["sub"] == "user@example.com"
    assert "exp" in payload
