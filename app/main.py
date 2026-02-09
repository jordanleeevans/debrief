import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from http import HTTPStatus
from app.core.settings import settings
from app.events import EventDispatcher
from app.commands import CommandBus
from app.services.discord import bot
from app.models.schemas import GameStatsResponse
from app.handlers import (
    register_gemini_command_handlers,
    register_mongodb_event_handlers,
    register_discord_event_handlers,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create dispatcher and command bus instances
event_dispatcher = EventDispatcher()
command_bus = CommandBus()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initialising start up configurations.")

    # Assign dispatcher and command bus to bot
    logger.info("Setting up command bus and event dispatcher...")
    bot.command_bus = command_bus
    bot.event_dispatcher = event_dispatcher

    # Register COMMAND handlers (1 handler per command)
    logger.info("Registering command handlers...")
    register_gemini_command_handlers(command_bus, event_dispatcher)
    logger.info("Command handlers registered successfully.")

    # Register EVENT subscribers (multiple subscribers per event)
    logger.info("Registering event subscribers...")
    register_mongodb_event_handlers(event_dispatcher)
    register_discord_event_handlers(event_dispatcher, bot)
    logger.info("Event subscribers registered successfully.")

    try:
        logger.info("Starting Discord bot...")
        asyncio.create_task(bot.start(settings.DISCORD_BOT_TOKEN))
        # Give the bot a moment to start connecting
        await asyncio.sleep(1)
        logger.info("Discord bot task created successfully.")
    except Exception as e:
        logger.error(f"Error starting Discord bot: {str(e)}", exc_info=True)

    yield

    try:
        logger.info("Closing Discord bot...")
        await bot.close()
        logger.info("Discord bot closed successfully.")
    except Exception as e:
        logger.error(f"Error closing Discord bot: {str(e)}", exc_info=True)


app = FastAPI(title="Debfrief API", version="1.0.0", lifespan=lifespan)


@app.get("/")
def health_check():
    return HTTPStatus.OK


@app.post("/schemas/test")
def test_game_stats(game_stats: GameStatsResponse):
    return game_stats
