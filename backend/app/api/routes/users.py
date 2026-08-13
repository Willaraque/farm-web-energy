from bson.errors import InvalidId
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.repositories.users import (
    create_one_user,
    delete_user,
    get_all_users,
    get_one_user,
    get_one_user_id,
    get_user_by_phone,
    update_user,
)
from app.schemas.models import CreateUser, UpdateUser, User
from app.repositories.tokens import get_user_active_current
from app.schemas.models import UserInDB

app_users = APIRouter(prefix="/api/users", tags=["users"])


@app_users.post("/create", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(payload: CreateUser) -> dict:
    payload.username = payload.username.strip().lower()
    if await get_one_user(payload):
        raise HTTPException(status.HTTP_409_CONFLICT, "El usuario ya existe")
    if payload.tel and await get_user_by_phone(payload.tel):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "No se pudo crear la cuenta con esos datos"
        )
    return await create_one_user(payload.model_dump())


@app_users.get("", response_model=list[User])
async def list_users(
    current: Annotated[UserInDB, Depends(get_user_active_current)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[User]:
    require_admin(current)
    return await get_all_users(skip=skip, limit=limit)


@app_users.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str, current: Annotated[UserInDB, Depends(get_user_active_current)]
) -> dict:
    require_self_or_admin(user_id, current)
    try:
        document = await get_one_user_id(user_id)
    except InvalidId as error:
        raise HTTPException(400, "Identificador de usuario inválido") from error
    if not document:
        raise HTTPException(404, "Usuario no encontrado")
    return document


@app_users.put("/update/{user_id}", response_model=User)
async def put_user(
    user_id: str,
    payload: UpdateUser,
    current: Annotated[UserInDB, Depends(get_user_active_current)],
) -> dict:
    require_self_or_admin(user_id, current)
    try:
        document = await update_user(user_id, payload)
    except InvalidId as error:
        raise HTTPException(400, "Identificador de usuario inválido") from error
    if not document:
        raise HTTPException(404, "Usuario no encontrado")
    return document


@app_users.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    user_id: str, current: Annotated[UserInDB, Depends(get_user_active_current)]
) -> None:
    require_self_or_admin(user_id, current)
    try:
        deleted = await delete_user(user_id)
    except InvalidId as error:
        raise HTTPException(400, "Identificador de usuario inválido") from error
    if not deleted:
        raise HTTPException(404, "Usuario no encontrado")


def require_admin(user: UserInDB) -> None:
    if user.tipo.casefold() != "admin":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Se requieren permisos de administrador"
        )


def require_self_or_admin(user_id: str, user: UserInDB) -> None:
    if str(user.id) != user_id and user.tipo.casefold() != "admin":
        # Do not reveal whether another user's identifier exists.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
