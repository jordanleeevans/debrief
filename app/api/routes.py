import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.shared.auth.dependencies import get_current_user
from app.shared.db.mongo import db
from app.shared.repositories import MatchRepository, serialize_mongo_documents

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/matches', tags=['matches'])


def get_match_repository() -> MatchRepository:
	"""Dependency to get MatchRepository instance"""
	return MatchRepository(db)


@router.get('')
async def list_matches(
	limit: int = Query(10, ge=1, le=100),
	skip: int = Query(0, ge=0),
	current_user_id: int = Depends(get_current_user),
	repo: MatchRepository = Depends(get_match_repository),
):
	"""List all matches for the current user with pagination (requires authentication)"""
	try:
		matches = await repo.list_by_user(discord_user_id=current_user_id, limit=limit, skip=skip)
		serialized_matches = serialize_mongo_documents(matches)
		return {'matches': serialized_matches, 'count': len(matches), 'skip': skip, 'limit': limit}
	except Exception as e:
		logger.error(f'Error listing matches: {str(e)}', exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))
