from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.schemas.models import User, UserInDB
from app.core.mongo import db_token, db_user
from app.core.config import settings
from app.core.database import run_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def credentials_error() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "No se pudieron validar las credenciales", {"WWW-Authenticate": "Bearer"})


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    if not settings.access_token_secret: raise RuntimeError("ACCESS_TOKEN_SECRET no está configurado")
    expires = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    return jwt.encode({**data, "exp": expires}, settings.access_token_secret, algorithm=settings.algorithm)


create_refresh_token = create_access_token


async def get_user(username: str) -> UserInDB | None:
    document = await run_collection(db_user, "find_one", {"username": username})
    return UserInDB(**document) if document else None


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str) -> UserInDB | None:
    user = await get_user(username.strip().lower())
    return user if user and await verify_password(password, user.password) else None


async def save_token(user_id: str | ObjectId, username: str, token: dict) -> dict:
    object_id = ObjectId(user_id)
    document = {"_id": object_id, "username": username, **token}
    await run_collection(db_token, "replace_one", {"_id": object_id}, document, upsert=True)
    document["_id"] = str(object_id)
    return document


async def update_token(current_token: str, changes: dict) -> dict | None:
    result = await run_collection(db_token, "find_one_and_update", {"access_token": current_token}, {"$set": changes}, return_document=True)
    if result: result["_id"] = str(result["_id"])
    return result


async def get_token(user_id: str, refresh_token: str) -> dict | None:
    return await run_collection(db_token, "find_one", {"_id": ObjectId(user_id), "refresh_token": refresh_token})


async def verify_refresh_token(refresh_token: str) -> dict:
    try:
        return jwt.decode(refresh_token, settings.access_token_secret, algorithms=[settings.algorithm])
    except jwt.PyJWTError as error:
        raise credentials_error() from error


async def get_user_current(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    try:
        payload = jwt.decode(token, settings.access_token_secret, algorithms=[settings.algorithm])
        username = payload.get("sub")
    except jwt.PyJWTError as error:
        raise credentials_error() from error
    if not username or not (user := await get_user(username)): raise credentials_error()
    return user


async def get_user_active_current(user: UserInDB = Depends(get_user_current)) -> UserInDB:
    if not user.active: raise HTTPException(403, "Usuario inactivo")
    return user


async def verify_token(token: str) -> dict[str, bool]:
    try: jwt.decode(token, settings.access_token_secret, algorithms=[settings.algorithm]); return {"valid": True}
    except jwt.PyJWTError: return {"valid": False}


async def drop_tokenBD(token_id: str) -> dict[str, bool]:
    try: result = await run_collection(db_token, "delete_one", {"_id": ObjectId(token_id)})
    except InvalidId: return {"valid": False}
    return {"valid": result.deleted_count == 1}
