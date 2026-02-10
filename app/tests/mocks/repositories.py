from app.models.schemas import MatchDocument, MongoPipeline


class FakeMatchRepository:
	"""A fake match repository for testing purposes"""

	def __init__(self, initial_matches: list[dict] = None):
		self.matches = initial_matches if initial_matches is not None else []

	async def insert_one(self, match_data: MatchDocument) -> str:
		"""Simulate saving match data to MongoDB"""
		if not isinstance(match_data, MatchDocument):
			raise ValueError('match_data must be an instance of MatchDocument')
		self.matches.append(match_data.model_dump())
		return str(len(self.matches) - 1)

	async def aggregate(self, pipeline: dict) -> list[dict]:
		"""Simulate running an aggregation pipeline"""
		# Validate the pipeline using MongoPipeline
		mp = MongoPipeline.model_validate(pipeline)

		# Start with all matches
		result = list(self.matches)

		# Process each stage in the pipeline
		for stage in mp.stages:
			if stage.operator == '$match':
				# Filter matches based on the expression
				result = [
					match
					for match in result
					if all(match.get(key) == value for key, value in stage.expression.items())
				]
			elif stage.operator == '$skip':
				# Skip specified number of documents
				result = result[stage.expression :]
			elif stage.operator == '$limit':
				# Limit to specified number of documents
				result = result[: stage.expression]

		return result

	async def list_by_user(
		self, discord_user_id: int, limit: int = 10, skip: int = 0
	) -> list[dict]:
		"""List matches for a specific user with pagination"""
		pipeline = {
			'stages': [
				{'operator': '$match', 'expression': {'discord_user_id': discord_user_id}},
				{'operator': '$skip', 'expression': skip},
				{'operator': '$limit', 'expression': limit},
			]
		}
		return await self.aggregate(pipeline)
