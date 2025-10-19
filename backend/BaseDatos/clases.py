from Librerias.lib import *
from Librerias.vars import *
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, Union

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, field=None) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


#----------------- Clase para crear un producto -------------------

class Task(BaseModel):
    # id:Optional[str] = Field(default_factory=PyObjectId, alias='_id')
    name: str
    category:str
    price:str
    description: Optional[str] = None
    completed: bool = False
    class Config:
        population_by_name = True
        json_encoders = {ObjectId: str}

class UpdateTask(BaseModel):
    name: Optional[str]=None
    description: Optional[str] = None
    completed: Optional[bool] = None


#----------------- Clase para crear un Usuario -------------------

class CreateUser(BaseModel):
    # id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="id") 
    username:str
    password:str
    name:Optional[str] = None
    surname:Optional[str] = None
    tel:Optional[str] = None
    active:Optional[bool] = True
    tipo:Optional[str] = 'Energia'

class UpdateUser(BaseModel):
    username:Optional[str]=None
    password: Optional[str] = None
    name:Optional[str] = None
    surname:Optional[str] = None
    tel:Optional[str] = None
    active:Optional[bool] = True
    tipo:Optional[str] = 'Energia'


#----------------- Clase para el token -------------------
class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    username: str
    name: Optional[str] = None
    surname: Optional[str] = None
    tel: Optional[str] = None
    active: Optional[bool] = None
    tipo: Optional[str] = 'Energia'
    class Config:
        population_by_name = True
        json_encoders = {ObjectId: str}

class UserInDB(User):
    password:str

class Token(BaseModel):
    id: Optional[str] = Field(default_factory=PyObjectId, alias='_id')
    username:str
    access_token: str
    # refresh_token: str
    token_type: str = None # Si también estás manejando un refresh token, lo puedes incluir
    class Config:
        population_by_name = True
        json_encoders = {ObjectId: str}

class RefreshToken(BaseModel):
    id:Optional[str] = Field(default_factory=PyObjectId, alias='_id')
    refresh_token:str
    class Config:
        population_by_name = True
        json_encoders = {ObjectId: str}


#------------- Verificacion de los tokens ----------
class TokenData(BaseModel):
    token: str

class RefreshTokenData(BaseModel):
    refresh_token: str

class IdMongo(BaseModel):
    id:Optional[str] = Field(default_factory=PyObjectId, alias='_id')
    class Config:
        population_by_name = True
        json_encoders = {ObjectId: str}

#------------- Tabla de precios ----------
class MarketData(BaseModel):
    desde: str 
    hasta:str
    tipo:str = 'Precios-OMIE'
    mercados:Optional[list] = ['diario', 'intradiario']
    search: Optional[list] = ['prsec', 'prter']
    warning: Optional[bool] = False
    # Agrega los campos necesarios según tu estructur

class MarketDataResponse(BaseModel):
    Fecha: str
    Tipo: str
    Season:int
    Precio_Español:Union[int|float]