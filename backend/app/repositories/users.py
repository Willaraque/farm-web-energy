from bson import ObjectId
from passlib.context import CryptContext

from app.schemas.models import CreateUser, UpdateUser, User
from app.core.mongo import db_user
from app.core.database import find_documents, run_collection

password_context = CryptContext(
    schemes=["pbkdf2_sha256"], deprecated="auto", pbkdf2_sha256__default_rounds=50000
)


def encrypt_password(password: str) -> str:
    return password_context.hash(password)


async def create_one_user(user: dict) -> dict:
    document = {**user, "password": encrypt_password(user["password"])}
    result = await run_collection(db_user, "insert_one", document)
    return await run_collection(db_user, "find_one", {"_id": result.inserted_id})


async def get_one_user(client: CreateUser | UpdateUser) -> dict | None:
    return (
        await run_collection(db_user, "find_one", {"username": client.username})
        if client.username
        else None
    )


async def get_user_by_phone(phone: str) -> dict | None:
    return await run_collection(db_user, "find_one", {"tel": phone})


async def get_all_users(skip: int = 0, limit: int = 50) -> list[User]:
    return [
        User(**document)
        for document in await find_documents(db_user, {}, skip=skip, limit=limit)
    ]


async def get_one_user_id(user_id: str) -> dict | None:
    return await run_collection(db_user, "find_one", {"_id": ObjectId(user_id)})


async def update_user(user_id: str, data: UpdateUser) -> dict | None:
    changes = data.model_dump(exclude_none=True)
    if "password" in changes:
        changes["password"] = encrypt_password(changes["password"])
    result = await run_collection(
        db_user, "update_one", {"_id": ObjectId(user_id)}, {"$set": changes}
    )
    return (
        await run_collection(db_user, "find_one", {"_id": ObjectId(user_id)})
        if result.matched_count
        else None
    )


async def delete_user(user_id: str) -> bool:
    result = await run_collection(db_user, "delete_one", {"_id": ObjectId(user_id)})
    return result.deleted_count == 1
