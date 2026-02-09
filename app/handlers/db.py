import logging
from app.events import (
    GameStatsAnalyzed,
    MatchSaved,
    EventDispatcher,
)
from app.repositories import MatchRepository
from app.models.schemas import MatchDocument
from app.db.mongo import db

logger = logging.getLogger(__name__)


async def handle_game_stats_analyzed(
    event: GameStatsAnalyzed,
    dispatcher: EventDispatcher,
    matches_repository: MatchRepository = MatchRepository(db),
) -> None:
    """Handle GameStatsAnalyzed event by saving match data to MongoDB.

    This is an event subscriber - it reacts to something that already happened.
    """
    logger.info(
        f"Saving match data for user {event.discord_user_id}, message {event.discord_message_id}"
    )

    try:
        match_document = MatchDocument(
            discord_user_id=event.discord_user_id,
            discord_message_id=event.discord_message_id,
            discord_channel_id=event.discord_channel_id,
            game_stats=event.game_stats,
            created_at=event.timestamp,
        )

        match_id = await matches_repository.insert_one(match_document)

        logger.info(f"Successfully saved match with ID: {match_id}")

        # Emit MatchSaved EVENT for other subscribers
        saved_event = MatchSaved(
            match_id=match_id,
            discord_user_id=event.discord_user_id,
            discord_message_id=event.discord_message_id,
            discord_channel_id=event.discord_channel_id,
            game_stats=event.game_stats,
        )
        await dispatcher.emit(saved_event)

    except Exception as e:
        logger.error(f"Error saving match to MongoDB: {str(e)}", exc_info=True)
        raise


def register_mongodb_event_handlers(dispatcher: EventDispatcher) -> None:
    """Register event subscribers for MongoDB persistence.

    These handlers react to events that have already happened.
    Events can have multiple subscribers.
    """
    dispatcher.subscribe(
        GameStatsAnalyzed, lambda event: handle_game_stats_analyzed(event, dispatcher)
    )
    logger.info("Registered MongoDB event handlers")
