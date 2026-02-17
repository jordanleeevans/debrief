import logging
from app.bot.commands import AnalyzeImagesCommand, QueryDatabaseCommand
from app.bot.events import GameStatsAnalyzed, QueryExecuted, EventDispatcher
from app.shared.services.gemini import GeminiClient
from app.shared.core.settings import settings

logger = logging.getLogger(__name__)


async def handle_analyze_images_command(
    command: AnalyzeImagesCommand,
    dispatcher: EventDispatcher,
    client: GeminiClient = GeminiClient,
) -> None:
    """Handle command to analyze images using Gemini AI.

    This is a command handler - it executes the command and emits events
    to notify other parts of the system about what happened.
    """
    logger.info(
        f"Analyzing images for user {command.discord_user_id}, message {command.discord_message_id}"
    )

    try:
        gemini_client = client(api_key=settings.GEMINI_API_KEY)
        game_stats = await gemini_client.generate_game_stats(
            command.image_one, command.image_two
        )

        logger.info(f"Successfully analyzed stats: {game_stats.model_dump()}")

        # Emit GameStatsAnalyzed EVENT for other handlers to process
        analyzed_event = GameStatsAnalyzed(
            game_stats=game_stats,
            discord_user_id=command.discord_user_id,
            discord_message_id=command.discord_message_id,
            discord_channel_id=command.discord_channel_id,
        )
        await dispatcher.emit(analyzed_event)

    except Exception as e:
        logger.error(f"Error analyzing images: {str(e)}", exc_info=True)
        raise


async def handle_query_database_command(
    command: QueryDatabaseCommand,
    dispatcher: EventDispatcher,
    client: GeminiClient = GeminiClient,
    repository=None,
) -> None:
    """Handle command to query database using natural language.

    This is a command handler - it executes the command and emits events
    to notify other parts of the system about what happened.
    """
    logger.info(
        f"Handling database query for user {command.discord_user_id}, message {command.discord_message_id}"
    )

    try:
        # Import repository if not provided (for production use)
        if repository is None:
            from app.shared.db.mongo import db
            from app.shared.repositories import MatchRepository

            repository = MatchRepository(db)

        # Generate MongoDB query using Gemini
        gemini_client = client(api_key=settings.GEMINI_API_KEY)
        db_query_response = await gemini_client.generate_db_query(command.query)

        logger.info(f"Successfully got Gemini query response: {db_query_response}")

        # Execute the query - db_query_response is already a dict from response.json()
        result = await repository.aggregate(db_query_response)

        logger.info(f"MongoDB aggregation result: {result}")

        # Emit QueryExecuted EVENT for other handlers to process
        query_executed_event = QueryExecuted(
            query=command.query,
            db_response=result,
            discord_user_id=command.discord_user_id,
            discord_message_id=command.discord_message_id,
            discord_channel_id=command.discord_channel_id,
        )
        await dispatcher.emit(query_executed_event)

    except Exception as e:
        logger.error(f"Error handling database query: {str(e)}", exc_info=True)
        raise


def register_gemini_command_handlers(command_bus, dispatcher: EventDispatcher) -> None:
    """Register command handlers for Gemini-related commands.

    Command handlers execute business logic and emit events.
    Each command has exactly one handler.
    """
    command_bus.register(
        AnalyzeImagesCommand,
        lambda cmd: handle_analyze_images_command(cmd, dispatcher),
    )
    command_bus.register(
        QueryDatabaseCommand,
        lambda cmd: handle_query_database_command(cmd, dispatcher),
    )
    logger.info("Registered Gemini command handlers")
