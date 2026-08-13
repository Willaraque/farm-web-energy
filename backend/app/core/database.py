from __future__ import annotations

import asyncio
from typing import Any


def _is_async_collection(collection: Any) -> bool:
    """Detecta colecciones Motor sin acoplar los repositorios a su versión."""
    return collection.__class__.__module__.startswith("motor.")


async def run_collection(
    collection: Any,
    operation: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Ejecuta operaciones Mongo de Motor o PyMongo sin bloquear el event loop."""
    method = getattr(collection, operation)
    if _is_async_collection(collection):
        return await method(*args, **kwargs)
    return await asyncio.to_thread(method, *args, **kwargs)


async def find_documents(
    collection: Any, query: dict[str, Any], *, skip: int = 0, limit: int = 100
) -> list[dict[str, Any]]:
    """Materializa un cursor Motor o PyMongo de forma segura."""
    if _is_async_collection(collection):
        cursor = collection.find(query)
        length = None
        if hasattr(cursor, "skip"):
            cursor = cursor.skip(skip).limit(limit)
            length = limit
        return await cursor.to_list(length=length)

    def materialize() -> list[dict[str, Any]]:
        cursor = collection.find(query)
        if hasattr(cursor, "skip"):
            cursor = cursor.skip(skip).limit(limit)
            return list(cursor)
        return list(cursor)[skip : skip + limit]

    return await asyncio.to_thread(materialize)
