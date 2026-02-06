from pymongo import AsyncMongoClient
from app.core.settings import settings

client = AsyncMongoClient(settings.MONGODB_URI)
db = client.get_database(settings.MONGODB_DB)


class FakeCollection:
    """A fake collection for testing purposes"""

    def __init__(self):
        self.documents = []

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.documents:
            raise StopAsyncIteration
        return self.documents.pop(0)

    async def insert_one(self, document):
        self.documents.append(document)
        return {"inserted_id": len(self.documents) - 1}


class FakeAsyncDatabase:
    """A fake async database for testing purposes"""

    def __init__(self):
        self.collections = FakeCollection()

    def get_collection(self, name):
        if name not in self.collections:
            self.collections[name] = []
        return self.collections[name]

    def insert_one(self, document):
        self.collections.setdefault("matches", []).append(document)
        return {"inserted_id": len(self.collections["matches"]) - 1}


class FakeAsyncMongoClient:
    """A fake async MongoDB client for testing purposes"""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.db = FakeAsyncDatabase()

    def get_database(self, name=None):
        return self.db
