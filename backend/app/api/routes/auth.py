from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.repositories.tokens import authenticate_user, create_access_token, drop_tokenBD, get_user_active_current, save_token, verify_token
from app.schemas.models import IdMongo, Token, TokenData, User, UserInDB

app_tokens = APIRouter(tags=["authentication"])


@app_tokens.post("/token", response_model=Token)
async def login_for_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user = await authenticate_user(form.username, form.password)
    if not user: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token({"sub": user.username}, timedelta(minutes=settings.access_token_expire_minutes))
    return await save_token(user.id, user.username, {"access_token": token, "token_type": "bearer"})


@app_tokens.get("/users/me", response_model=User)
async def read_users_me(user: Annotated[UserInDB, Depends(get_user_active_current)]) -> User:
    return User.model_validate(user.model_dump(exclude={"password"}))


@app_tokens.post("/verify-token")
async def verify_token_endpoint(data: TokenData) -> dict[str, bool]:
    result = await verify_token(data.token)
    if not result["valid"]: raise HTTPException(401, "Token inválido")
    return result


@app_tokens.delete("/delete-token")
async def delete_token(data: IdMongo) -> dict[str, bool]:
    result = await drop_tokenBD(data.id)
    if not result["valid"]: raise HTTPException(404, "Token no encontrado")
    return result
