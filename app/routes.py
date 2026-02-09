import logging
from fastapi import APIRouter, HTTPException, Query
from app.repositories import MatchRepository, serialize_mongo_documents
from app.db.mongo import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("")
async def list_matches(
    limit: int = Query(10, ge=1, le=100), skip: int = Query(0, ge=0)
):
    """List all matches with pagination"""
    try:
        repo = MatchRepository(db)
        pipeline = {
            "stages": [
                {"operator": "$skip", "expression": skip},
                {"operator": "$limit", "expression": limit},
            ]
        }
        matches = await repo.aggregate(pipeline)
        # Convert ObjectId and other BSON types to JSON-serializable formats
        serialized_matches = serialize_mongo_documents(matches)
        return {
            "matches": serialized_matches,
            "count": len(matches),
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing matches: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
