import logging
from app.events import MatchSaved, EventDispatcher

logger = logging.getLogger(__name__)

# Store Discord context for sending messages back
_discord_contexts: dict[int, object] = {}


def store_discord_context(message_id: int, ctx: object) -> None:
    """Store Discord context for later message sending"""
    _discord_contexts[message_id] = ctx


async def handle_match_saved_discord_response(event: MatchSaved) -> None:
    """Handle sending analysis results back to Discord after MongoDB save"""
    logger.info(f"Sending results to Discord for message {event.discord_user_id}")

    try:
        ctx = _discord_contexts.get(event.discord_message_id)
        if ctx is None:
            logger.warning(f"No Discord context found for match {event.match_id}")
            return

        # Send results back to Discord
        result_message = (
            f"✅ Analysis complete! Match saved with ID: `{event.match_id}`\n"
            f"```json\n{event.game_stats.model_dump_json(indent=2)}\n```"
        )
        await ctx.send(result_message)

        # Clean up context
        del _discord_contexts[event.discord_message_id]

    except Exception as e:
        logger.error(f"Error sending Discord response: {str(e)}", exc_info=True)


def register_discord_response_handler(dispatcher: EventDispatcher) -> None:
    """Register Discord response handler"""
    dispatcher.subscribe(MatchSaved, handle_match_saved_discord_response)
    logger.info("Registered Discord response handler")
