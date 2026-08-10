from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, status

from app.repositories.users import create_one_user, delete_user, get_all_users, get_one_user, get_one_user_id, update_user
from app.schemas.models import CreateUser, UpdateUser, User

app_users = APIRouter(prefix="/api/users", tags=["users"])


@app_users.post("/create", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(payload: CreateUser) -> dict:
    payload.username = payload.username.strip().lower()
    if await get_one_user(payload): raise HTTPException(status.HTTP_409_CONFLICT, "El usuario ya existe")
    return await create_one_user(payload.model_dump())


@app_users.get("", response_model=list[User])
async def list_users() -> list[User]:
    return await get_all_users()


@app_users.get("/{user_id}", response_model=User)
async def get_user(user_id: str) -> dict:
    try: document = await get_one_user_id(user_id)
    except InvalidId as error: raise HTTPException(400, "Identificador de usuario inválido") from error
    if not document: raise HTTPException(404, "Usuario no encontrado")
    return document


@app_users.put("/update/{user_id}", response_model=User)
async def put_user(user_id: str, payload: UpdateUser) -> dict:
    try: document = await update_user(user_id, payload)
    except InvalidId as error: raise HTTPException(400, "Identificador de usuario inválido") from error
    if not document: raise HTTPException(404, "Usuario no encontrado")
    return document


@app_users.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(user_id: str) -> None:
    try: deleted = await delete_user(user_id)
    except InvalidId as error: raise HTTPException(400, "Identificador de usuario inválido") from error
    if not deleted: raise HTTPException(404, "Usuario no encontrado")
