from bson import ObjectId

from app.schemas.models import Task, UpdateTask
from app.core.mongo import db_products
from app.core.database import find_documents, run_collection


async def get_one_task_id(task_id: str) -> dict | None:
    document = await run_collection(db_products, "find_one", {"_id": ObjectId(task_id)})
    if document:
        document["_id"] = str(document["_id"])
    return document


async def get_one_task(name: str) -> dict | None:
    return await run_collection(db_products, "find_one", {"name": name})


async def get_all_tasks(skip: int = 0, limit: int = 100) -> list[dict]:
    tasks = []
    for document in await find_documents(db_products, {}, skip=skip, limit=limit):
        document["_id"] = str(document["_id"])
        tasks.append(document)
    return tasks


async def create_one_task(task: dict) -> dict:
    result = await run_collection(db_products, "insert_one", task)
    document = await run_collection(
        db_products, "find_one", {"_id": result.inserted_id}
    )
    document["_id"] = str(document["_id"])
    return document


async def update_task(task_id: str, data: UpdateTask) -> dict | None:
    changes = data.model_dump(exclude_none=True)
    result = await run_collection(
        db_products, "update_one", {"_id": ObjectId(task_id)}, {"$set": changes}
    )
    return await get_one_task_id(task_id) if result.matched_count else None


async def delete_one_task(task_id: str) -> bool:
    result = await run_collection(db_products, "delete_one", {"_id": ObjectId(task_id)})
    return result.deleted_count == 1
