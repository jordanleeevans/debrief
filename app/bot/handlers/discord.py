import logging
from app.bot.events import MatchSaved, QueryExecuted, EventDispatcher

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


async def handle_match_saved_event(bot, event: MatchSaved):
    """Event subscriber that sends match saved notification to Discord.

    This is an event subscriber - it reacts to something that already happened.
    """
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


async def handle_query_executed_event(bot, event: QueryExecuted):
    """Event subscriber that sends query results to Discord.

    This is an event subscriber - it reacts to something that already happened.
    """
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
        f"✅ Query complete for <@{event.discord_user_id}>! Database response:\n"
        f"```json\n{event.db_response}\n```"
    )

    try:
        await channel.send(content=result_message)
        logger.info(f"Sent query result to channel {event.discord_channel_id}")
    except Exception as e:
        logger.error(
            f"Failed to send query result to channel {event.discord_channel_id}: {e}",
            exc_info=True,
        )


def register_discord_event_handlers(dispatcher: EventDispatcher, bot) -> None:
    """Register Discord event subscribers.

    These subscribers react to events and send messages back to Discord.
    Events can have multiple subscribers.
    """
    dispatcher.subscribe(MatchSaved, lambda event: handle_match_saved_event(bot, event))
    dispatcher.subscribe(
        QueryExecuted, lambda event: handle_query_executed_event(bot, event)
    )
    logger.info("Registered Discord event handlers")
