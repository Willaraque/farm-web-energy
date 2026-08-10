import asyncio

from app.core.database import find_documents, run_collection


class SyncCursor:
    def __iter__(self):
        return iter([{"name": "one"}, {"name": "two"}])


class SyncCollection:
    def find_one(self, query):
        return {"username": query["username"]}

    def find(self, query):
        assert query == {}
        return SyncCursor()


class AsyncCursor:
    async def to_list(self, length=None):
        assert length is None
        return [{"name": "async"}]


class AsyncCollection:
    __module__ = "motor.motor_asyncio"

    async def find_one(self, query):
        return {"username": query["username"]}

    def find(self, query):
        assert query == {}
        return AsyncCursor()


def test_sync_pymongo_operations_are_awaitable() -> None:
    collection = SyncCollection()
    result = asyncio.run(run_collection(collection, "find_one", {"username": "will"}))
    documents = asyncio.run(find_documents(collection, {}))
    assert result == {"username": "will"}
    assert len(documents) == 2


def test_async_motor_operations_are_awaitable() -> None:
    collection = AsyncCollection()
    result = asyncio.run(run_collection(collection, "find_one", {"username": "will"}))
    documents = asyncio.run(find_documents(collection, {}))
    assert result == {"username": "will"}
    assert documents == [{"name": "async"}]
