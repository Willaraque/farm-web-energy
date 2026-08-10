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


async def find_documents(collection: Any, query: dict[str, Any]) -> list[dict[str, Any]]:
    """Materializa un cursor Motor o PyMongo de forma segura."""
    if _is_async_collection(collection):
        return await collection.find(query).to_list(length=None)
    return await asyncio.to_thread(lambda: list(collection.find(query)))
