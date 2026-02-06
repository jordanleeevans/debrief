import logging
from app.events import dispatcher, AnalyzeImagesRequested, GameStatsAnalyzed
from app.services.gemini import GeminiClient
from app.core.settings import settings

logger = logging.getLogger(__name__)


async def handle_analyze_images(event: AnalyzeImagesRequested, client: GeminiClient = GeminiClient) -> None:
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
        )
        await dispatcher.emit(analyzed_event)

    except Exception as e:
        logger.error(f"Error analyzing images: {str(e)}", exc_info=True)
        raise


def register_gemini_handlers() -> None:
    """Register Gemini analysis handler"""
    dispatcher.subscribe(AnalyzeImagesRequested, handle_analyze_images)
    logger.info("Registered Gemini analysis handler")
