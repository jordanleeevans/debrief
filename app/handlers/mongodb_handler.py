import logging
from app.events import GameStatsAnalyzed, MatchSaved, EventDispatcher
from app.db.mongo import db
from pymongo.asynchronous.database import AsyncDatabase

logger = logging.getLogger(__name__)


async def handle_match_saved(
    event: GameStatsAnalyzed, dispatcher: EventDispatcher, db: AsyncDatabase = db
) -> None:
    """Handle saving analyzed game stats to MongoDB"""
    logger.info(
        f"Saving match data for user {event.discord_user_id}, message {event.discord_message_id}"
    )

    try:
        # Prepare match document
        match_document = {
            "discord_user_id": event.discord_user_id,
            "discord_message_id": event.discord_message_id,
            "game_stats": event.game_stats.model_dump(),
            "created_at": event.timestamp,
        }

        # Insert into MongoDB
        matches_collection = db.get_collection("matches")
        result = await matches_collection.insert_one(match_document)

        match_id = str(result.inserted_id)
        logger.info(f"Successfully saved match with ID: {match_id}")

        # Emit MatchSaved event for any other handlers
        saved_event = MatchSaved(
            match_id=match_id,
            discord_user_id=event.discord_user_id,
            discord_message_id=event.discord_message_id,
            game_stats=event.game_stats,
        )
        await dispatcher.emit(saved_event)

    except Exception as e:
        logger.error(f"Error saving match to MongoDB: {str(e)}", exc_info=True)
        raise


def register_mongodb_handlers(dispatcher: EventDispatcher) -> None:
    """Register MongoDB persistence handler"""
    dispatcher.subscribe(
        GameStatsAnalyzed, lambda event: handle_match_saved(event, dispatcher)
    )
    logger.info("Registered MongoDB persistence handler")
