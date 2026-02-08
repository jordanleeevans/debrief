import logging
from app.events import MatchSaved, EventDispatcher

logger = logging.getLogger(__name__)


def get_channel_from_cache(bot, channel_id: int):
    """Helper function to get channel from cache"""
    channel = bot.get_channel(channel_id)
    if channel is None:
        logger.debug(f"Channel {channel_id} not found in cache")
    else:
        logger.debug(f"Channel {channel_id} found in cache")
    return channel


async def fetch_channel_from_api(bot, channel_id: int):
    """Helper function to fetch channel from Discord API"""
    try:
        channel = await bot.fetch_channel(channel_id)
        logger.debug(f"Channel {channel_id} fetched from API successfully")
        return channel
    except Exception as e:
        logger.error(
            f"Failed to fetch channel {channel_id} from API: {e}", exc_info=True
        )
        return None


async def handle_match_saved(bot, event: MatchSaved):
    """Helper function to send message to Discord channel"""
    channel = get_channel_from_cache(bot, event.discord_channel_id)
    if channel is None:
        logger.info(
            f"Channel {event.discord_channel_id} not in cache, fetching from API..."
        )
        channel = await fetch_channel_from_api(bot, event.discord_channel_id)

    if channel is None:
        logger.error(
            f"Unable to send message: Channel {event.discord_channel_id} could not be found after API fetch"
        )
        return

    result_message = (
        f"✅ Analysis complete! Match saved with ID: `{event.match_id}`\n"
        f"```json\n{event.game_stats.model_dump_json(indent=2)}\n```"
    )

    try:
        await channel.send(content=result_message)
        logger.info(f"Sent message to channel {event.discord_channel_id} successfully")
    except Exception as e:
        logger.error(
            f"Failed to send message to channel {event.discord_channel_id}: {e}",
            exc_info=True,
        )


async def handle_query_result(bot, event):
    """Return response from Gemini query back to Discord channel"""
    pass


def register_discord_response_handler(dispatcher: EventDispatcher, bot) -> None:
    """Register Discord response handler which uses primitive IDs and the bot

    This avoids storing the full Discord `ctx` object and keeps the event
    pipeline decoupled. The handler fetches the channel by ID when it needs
    to send a reply.
    """
    dispatcher.subscribe(MatchSaved, lambda event: handle_match_saved(bot, event))
    logger.info("Registered Discord response handler")
