from pymongo.asynchronous.database import AsyncDatabase
from app.models.schemas import MatchDocument


class MatchRepository:
    """Repository for managing match data in MongoDB"""

    def __init__(self, db):
        self.db: AsyncDatabase = db

    async def insert_one(self, match_data: MatchDocument) -> str:
        """Save analyzed match data to MongoDB"""
        if not isinstance(match_data, MatchDocument):
            raise ValueError("match_data must be an instance of MatchDocument")
        result = await self.db.matches.insert_one(match_data.model_dump())
        return result.inserted_id


class FakeMatchRepository:
    """A fake match repository for testing purposes"""

    def __init__(self):
        self.matches = []

    async def insert_one(self, match_data: MatchDocument) -> str:
        """Simulate saving match data to MongoDB"""
        if not isinstance(match_data, MatchDocument):
            raise ValueError("match_data must be an instance of MatchDocument")
        self.matches.append(match_data.model_dump())
        return len(self.matches) - 1
