from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from bson import ObjectId
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)


class MongoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @field_serializer("id", check_fields=False, when_used="json")
    def serialize_id(self, value: str | ObjectId | None) -> str | None:
        return str(value) if value is not None else None


class Task(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    price: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = False

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: str) -> str:
        return validate_price(value)


class UpdateTask(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    price: str | None = Field(default=None, min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None

    @field_validator("price")
    @classmethod
    def validate_price_field(cls, value: str | None) -> str | None:
        return validate_price(value)


class CreateUser(BaseModel):
    username: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=80)
    surname: str | None = Field(default=None, max_length=120)
    tel: str | None = Field(default=None, pattern=r"^\+[1-9]\d{7,14}$")


class PhoneRequest(BaseModel):
    phone: str = Field(pattern=r"^\+[1-9]\d{7,14}$")


class OtpVerify(PhoneRequest):
    challenge_id: str = Field(min_length=20, max_length=120)
    code: str = Field(pattern=r"^\d{6}$")


class ResetPassword(BaseModel):
    reset_token: str = Field(min_length=20, max_length=200)
    password: str = Field(min_length=10, max_length=128)


class OAuthExchange(BaseModel):
    code: str = Field(min_length=20, max_length=200)


class UpdateUser(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=254)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=80)
    surname: str | None = Field(default=None, max_length=120)
    tel: str | None = Field(default=None, max_length=30)


class User(MongoModel):
    id: str | ObjectId | None = Field(default=None, alias="_id")
    username: str
    name: str | None = None
    surname: str | None = None
    tel: str | None = None
    active: bool = True
    tipo: str = "Energia"


class UserInDB(User):
    password: str


class Token(MongoModel):
    id: str | ObjectId | None = Field(default=None, alias="_id")
    username: str
    access_token: str
    token_type: str = "bearer"


class RefreshToken(MongoModel):
    id: str | ObjectId | None = Field(default=None, alias="_id")
    refresh_token: str


class TokenData(BaseModel):
    token: str


class RefreshTokenData(BaseModel):
    refresh_token: str


class IdMongo(BaseModel):
    id: str = Field(alias="_id")


class MarketData(BaseModel):
    desde: str
    hasta: str
    tipo: str = "Precios-OMIE"
    mercados: list[str] = Field(default_factory=lambda: ["diario", "intradiario"])
    search: list[str] = Field(default_factory=lambda: ["prsec", "prter"])
    warning: bool = False

    @model_validator(mode="after")
    def validate_period(self):
        try:
            start, end = date.fromisoformat(self.desde), date.fromisoformat(self.hasta)
        except ValueError as error:
            raise ValueError("desde and hasta must use YYYY-MM-DD") from error
        if end < start:
            raise ValueError("hasta cannot be before desde")
        from app.core.config import settings

        if (end - start).days > settings.max_market_range_days:
            raise ValueError(f"Maximum period is {settings.max_market_range_days} days")
        return self


def validate_price(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("price must be numeric") from error
    if not number.is_finite() or abs(number) > Decimal("1000000000"):
        raise ValueError("price is outside the allowed range")
    return value


class MarketDataResponse(BaseModel):
    Fecha: str
    Tipo: str
    Season: int
    Precio_Español: int | float


Document = dict[str, Any]
