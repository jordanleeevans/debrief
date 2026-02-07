from app.models.schemas import MatchDocument


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
