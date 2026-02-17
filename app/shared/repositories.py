import logging
from typing import Any

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.shared.models.schemas import MatchDocument, MongoPipeline

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
			raise ValueError('match_data must be an instance of MatchDocument')
		result = await self.db.matches.insert_one(match_data.model_dump())
		# Convert ObjectId to string to match expected return type
		return str(result.inserted_id)

	async def aggregate(self, pipeline: dict) -> list[dict]:
		"""Run an aggregation pipeline on the matches collection"""
		mp = MongoPipeline.model_validate(pipeline)
		pymongo_pipeline = [{s.operator: s.expression} for s in mp.stages]
		logger.info(f'Running MongoDB aggregation with pipeline: {pymongo_pipeline}')
		cursor = await self.db.matches.aggregate(pymongo_pipeline)
		return await cursor.to_list(length=None)

	async def list_by_user(
		self, discord_user_id: int, limit: int = 10, skip: int = 0
	) -> list[dict]:
		"""List matches for a specific user with pagination

		Args:
		    discord_user_id: Discord user ID to filter matches
		    limit: Maximum number of matches to return (1-100)
		    skip: Number of matches to skip for pagination

		Returns:
		    List of match documents for the specified user
		"""
		pipeline = {
			'stages': [
				{'operator': '$match', 'expression': {'discord_user_id': discord_user_id}},
				{'operator': '$skip', 'expression': skip},
				{'operator': '$limit', 'expression': limit},
			]
		}
		return await self.aggregate(pipeline)
