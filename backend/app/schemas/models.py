from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class MongoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @field_serializer("id", check_fields=False, when_used="json")
    def serialize_id(self, value: str | ObjectId | None) -> str | None:
        return str(value) if value is not None else None


class Task(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    price: str
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = False


class UpdateTask(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    price: str | None = None
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None


class CreateUser(BaseModel):
    username: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=80)
    surname: str | None = Field(default=None, max_length=120)
    tel: str | None = Field(default=None, max_length=30)
    active: bool = True
    tipo: str = "Energia"


class UpdateUser(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=254)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=80)
    surname: str | None = Field(default=None, max_length=120)
    tel: str | None = Field(default=None, max_length=30)
    active: bool | None = None
    tipo: str | None = None


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


class TokenData(BaseModel): token: str
class RefreshTokenData(BaseModel): refresh_token: str
class IdMongo(BaseModel): id: str = Field(alias="_id")


class MarketData(BaseModel):
    desde: str
    hasta: str
    tipo: str = "Precios-OMIE"
    mercados: list[str] = Field(default_factory=lambda: ["diario", "intradiario"])
    search: list[str] = Field(default_factory=lambda: ["prsec", "prter"])
    warning: bool = False


class MarketDataResponse(BaseModel):
    Fecha: str
    Tipo: str
    Season: int
    Precio_Español: int | float


Document = dict[str, Any]
