import logging
import asyncio
from app.shared.core.settings import settings
from app.bot.events import EventDispatcher
from app.bot.commands import CommandBus
from app.shared.services.discord import bot
from app.bot.handlers import (
    register_gemini_command_handlers,
    register_mongodb_event_handlers,
    register_discord_event_handlers,
)

logger = logging.getLogger(__name__)


def setup_handlers(command_bus: CommandBus, event_dispatcher: EventDispatcher):
    """Register all command handlers and event subscribers"""
    logger.info("Registering command handlers...")
    register_gemini_command_handlers(command_bus, event_dispatcher)

    logger.info("Registering event subscribers...")
    register_mongodb_event_handlers(event_dispatcher)
    register_discord_event_handlers(event_dispatcher, bot)

    logger.info("All handlers registered successfully.")


async def start_bot():
    """Start the Discord bot"""
    try:
        logger.info("Starting Discord bot...")
        asyncio.create_task(bot.start(settings.DISCORD_BOT_TOKEN))
        await asyncio.sleep(1)
        logger.info("Discord bot started successfully.")
    except Exception as e:
        logger.error(f"Error starting Discord bot: {str(e)}", exc_info=True)
        raise


async def stop_bot():
    """Stop the Discord bot"""
    try:
        logger.info("Stopping Discord bot...")
        await bot.close()
        logger.info("Discord bot stopped successfully.")
    except Exception as e:
        logger.error(f"Error stopping Discord bot: {str(e)}", exc_info=True)
