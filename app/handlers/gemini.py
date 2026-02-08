import logging
from app.events import AnalyzeImagesRequested, GameStatsAnalyzed, EventDispatcher
from app.events.events import GeminiQueryRequested
from app.services.gemini import GeminiClient
from app.core.settings import settings

logger = logging.getLogger(__name__)


async def handle_analyze_images(
    event: AnalyzeImagesRequested,
    dispatcher: EventDispatcher,
    client: GeminiClient = GeminiClient,
) -> None:
    """Handle image analysis request from Discord"""
    logger.info(
        f"Analyzing images for user {event.discord_user_id}, message {event.discord_message_id}"
    )

    try:
        gemini_client = client(api_key=settings.GEMINI_API_KEY)
        game_stats = await gemini_client.generate_game_stats(
            event.image_one, event.image_two
        )

         
        logger.info(f"Successfully analyzed stats: {game_stats.model_dump()}")

        # Emit GameStatsAnalyzed event for other handlers to process
        analyzed_event = GameStatsAnalyzed(
            game_stats=game_stats,
            discord_user_id=event.discord_user_id,
            discord_message_id=event.discord_message_id,
            discord_channel_id=event.discord_channel_id,
        )
        await dispatcher.emit(analyzed_event)

    except Exception as e:
        logger.error(f"Error analyzing images: {str(e)}", exc_info=True)
        raise

async def handle_gemini_query(
    event: GeminiQueryRequested,
    dispatcher: EventDispatcher,
    client: GeminiClient = GeminiClient,
) -> None:
    """Handle Gemini query request from Discord"""
    logger.info(
        f"Handling Gemini query for user {event.discord_user_id}, message {event.discord_message_id}"
    )

    try:
        gemini_client = client(api_key=settings.GEMINI_API_KEY)
        db_query_response = await gemini_client.query_database(event.query)

        logger.info(f"Successfully got Gemini query response: {db_query_response}")

        query_created = QueryGenerated(
            query=event.query,
            response=db_query_response,
            discord_user_id=event.discord_user_id,
            discord_message_id=event.discord_message_id,
            discord_channel_id=event.discord_channel_id,
        )
        await dispatcher.emit(query_created)
    except Exception as e:
        logger.error(f"Error handling Gemini query: {str(e)}", exc_info=True)
        raise


def register_gemini_handlers(dispatcher: EventDispatcher) -> None:
    """Register Gemini analysis handler"""
    dispatcher.subscribe(
        AnalyzeImagesRequested, lambda event: handle_analyze_images(event, dispatcher)
    )
    dispatcher.subscribe(
        GeminiQueryRequested, lambda event: handle_gemini_query(event, dispatcher)
    )
    logger.info("Registered Gemini analysis handler")
