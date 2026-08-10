import pytest
from pydantic import ValidationError

from app.schemas.models import CreateUser, MarketData


def test_market_defaults_are_not_shared() -> None:
    first = MarketData(desde="2026-01-01", hasta="2026-01-02")
    second = MarketData(desde="2026-01-01", hasta="2026-01-02")
    first.mercados.append("continuo")
    assert "continuo" not in second.mercados


def test_user_requires_secure_minimum_password_length() -> None:
    with pytest.raises(ValidationError):
        CreateUser(username="valid-user", password="short")
