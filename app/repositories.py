import logging
from typing import Any
from pymongo.asynchronous.database import AsyncDatabase
from app.models.schemas import MatchDocument, MongoPipeline
from bson import ObjectId

logger = logging.getLogger(__name__)


def serialize_mongo_documents(data: Any) -> Any:
    """Convert MongoDB ObjectId and other BSON types to JSON-serializable formats"""
    if isinstance(data, dict):
        return {key: serialize_mongo_documents(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_mongo_documents(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data


class MatchRepository:
    """Repository for managing match data in MongoDB"""

    def __init__(self, db: AsyncDatabase):
        self.db: AsyncDatabase = db

    async def insert_one(self, match_data: MatchDocument) -> str:
        """Save analyzed match data to MongoDB"""
        if not isinstance(match_data, MatchDocument):
            raise ValueError("match_data must be an instance of MatchDocument")
        result = await self.db.matches.insert_one(match_data.model_dump())
        # Convert ObjectId to string to match expected return type
        return str(result.inserted_id)

    async def aggregate(self, pipeline: dict) -> list[dict]:
        """Run an aggregation pipeline on the matches collection"""
        mp = MongoPipeline.model_validate(pipeline)
        pymongo_pipeline = [{s.operator: s.expression} for s in mp.stages]
        logger.info(f"Running MongoDB aggregation with pipeline: {pymongo_pipeline}")
        cursor = await self.db.matches.aggregate(pymongo_pipeline)
        return await cursor.to_list(length=None)
