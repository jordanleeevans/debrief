class MatchRepository:
    """Repository for managing match data in MongoDB"""

    def __init__(self, db):
        self.db = db

    async def insert_one(self, match_data) -> str:
        """Save analyzed match data to MongoDB"""
        result = await self.db.matches.insert_one(match_data)
        return result.inserted_id


class FakeMatchRepository:
    """A fake match repository for testing purposes"""

    def __init__(self):
        self.matches = []

    async def insert_one(self, match_data):
        """Simulate saving match data to MongoDB"""
        self.matches.append(match_data)
        return len(self.matches) - 1
