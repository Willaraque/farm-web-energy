from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, status

from app.repositories.products import create_one_task, delete_one_task, get_all_tasks, get_one_task, get_one_task_id, update_task
from app.schemas.models import Task, UpdateTask

task = APIRouter(prefix="/api/tasks", tags=["products"])


@task.get("")
async def get_tasks() -> list[dict]: return await get_all_tasks()


@task.post("", status_code=status.HTTP_201_CREATED)
async def create_task(payload: Task) -> dict:
    if await get_one_task(payload.name): raise HTTPException(409, "El producto ya existe")
    return await create_one_task(payload.model_dump())


@task.get("/{task_id}")
async def get_task(task_id: str) -> dict:
    try: document = await get_one_task_id(task_id)
    except InvalidId as error: raise HTTPException(400, "Identificador de producto inválido") from error
    if not document: raise HTTPException(404, "Producto no encontrado")
    return document


@task.put("/{task_id}")
async def put_task(task_id: str, payload: UpdateTask) -> dict:
    try: document = await update_task(task_id, payload)
    except InvalidId as error: raise HTTPException(400, "Identificador de producto inválido") from error
    if not document: raise HTTPException(404, "Producto no encontrado")
    return document


@task.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_task(task_id: str) -> None:
    try: deleted = await delete_one_task(task_id)
    except InvalidId as error: raise HTTPException(400, "Identificador de producto inválido") from error
    if not deleted: raise HTTPException(404, "Producto no encontrado")
